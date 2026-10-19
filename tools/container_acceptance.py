"""Build and exercise the real Docker artifact using disposable synthetic volumes.

Requires a Linux Docker daemon. Never reads .env, publishes host ports, contacts Ollama,
or reuses existing application volumes. Outputs sanitized machine-readable evidence.
"""

import argparse
import ipaddress
import json
import os
import secrets
import shutil

# The maintainer-only acceptance driver invokes the Docker CLI without a shell.
import subprocess  # nosec B404
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# A private per-container tmpfs mount, not a host temporary filename.
CONTAINER_TMPFS = "/tmp:size=32m,mode=1777"  # nosec B108


def ensure(condition, message="Container acceptance assertion failed"):
    if not condition:
        raise AssertionError(message)


class Acceptance:
    def __init__(self, image, output):
        self.executable = shutil.which("docker")
        if not self.executable:
            raise RuntimeError("Docker CLI is unavailable; container execution is not verified")
        self.image = image
        self.output = output
        self.prefix = "sd-acceptance-" + secrets.token_hex(6)
        self.containers = []
        self.volumes = []
        self.networks = []
        self.env = {
            "APP_ENV": "production",
            "HOST": "127.0.0.1",
            "PORT": "8787",
            "DATABASE_PATH": "/data/verification.db",
            "PUBLIC_URL": "https://pilot.example.org",
            "ADMIN_PASSWORD": secrets.token_urlsafe(32),
            "SESSION_SECRET": secrets.token_urlsafe(48),
            "EMAIL_DELIVERY_ENABLED": "false",
            "ENABLE_LOCAL_GENERATION": "false",
            "TRUSTED_PROXY": "127.0.0.1",
        }
        self.report = {
            "result": "FAIL",
            "checks": [],
            "public_https": "NOT_TESTED",
            "source_commit": os.getenv("GITHUB_SHA", "local-unrecorded"),
        }

    def docker(self, *args, expected=0):
        # Absolute CLI path and separate maintainer-supplied arguments; shell is disabled.
        process = subprocess.run(  # nosec B603
            [self.executable, *map(str, args)],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, **self.env},
            timeout=600,
        )
        if (process.returncode == 0) != (expected == 0):
            # No environment inspection or credential-bearing command line enters the report.
            raise RuntimeError(f"Docker {args[0]} failed: {process.stderr[-2500:]}")
        return process.stdout.strip()

    def checked(self, description):
        self.report["checks"].append(description)
        print("PASS: " + description, flush=True)

    def inspect(self, kind, identity):
        return json.loads(self.docker(kind, "inspect", identity))[0]

    def volume(self, suffix):
        name = self.prefix + "-" + suffix
        self.docker("volume", "create", name)
        self.volumes.append(name)
        return name

    def env_args(self):
        return [part for key in self.env for part in ("--env", key)]

    def start(self, suffix, volume, network="none", extra=()):
        name = self.prefix + "-" + suffix
        self.containers.append(name)
        self.docker(
            "run",
            "--detach",
            "--name",
            name,
            "--network",
            network,
            "--read-only",
            "--tmpfs",
            CONTAINER_TMPFS,
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--pids-limit",
            "128",
            "--memory",
            "512m",
            "--mount",
            f"type=volume,src={volume},dst=/data",
            *self.env_args(),
            *extra,
            self.image,
        )
        self.healthy(name)
        info = json.loads(self.docker("inspect", name))[0]
        ensure(not info["HostConfig"]["PortBindings"])
        ensure(info["HostConfig"]["ReadonlyRootfs"])
        ensure(info["HostConfig"]["Memory"] == 512 * 1024 * 1024)
        ensure(info["HostConfig"]["PidsLimit"] == 128)
        ensure(info["HostConfig"]["CapDrop"] == ["ALL"])
        return name

    def healthy(self, name):
        for _ in range(90):
            info = json.loads(self.docker("inspect", name))[0]
            if not info["State"]["Running"]:
                raise RuntimeError("Application container exited during startup")
            status = info["State"].get("Health", {}).get("Status")
            if status == "healthy":
                return
            if status == "unhealthy":
                raise RuntimeError("Image healthcheck reported unhealthy")
            time.sleep(1)
        raise RuntimeError("Image healthcheck did not become healthy in 90 seconds")

    def probe(self, name, action):
        return self.docker("exec", name, "python", "tools/container_acceptance_probe.py", action)

    def compose(self, directory):
        # Copy only configuration; relative env_file resolves to synthetic .env in this directory.
        shutil.copyfile(ROOT / "compose.yaml", directory / "compose.yaml")
        (directory / ".env").write_text(
            "\n".join(f"{key}={value}" for key, value in self.env.items())
            + "\nPUBLIC_HOST=pilot.example.org\nEDITOR_CIDR=127.0.0.1/32\n",
            encoding="utf-8",
        )
        values = json.loads(
            self.docker(
                "compose",
                "--project-directory",
                directory,
                "-f",
                directory / "compose.yaml",
                "config",
                "--format",
                "json",
            )
        )
        app = values["services"]["newsletter"]
        ensure(set(values["services"]) == {"newsletter", "proxy"})
        ensure(not app.get("ports") and app["read_only"])
        ensure(app["environment"]["ENABLE_LOCAL_GENERATION"] == "false")
        ensure(app["environment"]["EMAIL_DELIVERY_ENABLED"] == "false")
        ensure(app["cap_drop"] == ["ALL"] and app["pids_limit"] == 128)
        ensure(app["mem_limit"] == "536870912" or app["mem_limit"] == 536870912)
        ports = values["services"]["proxy"]["ports"]
        ensure({int(port["target"]) for port in ports} == {80, 443})
        self.checked(
            "Production Compose validates with synthetic configuration; app and Ollama have no published ports"
        )

    def proxy(self, directory, volume):
        caddy_image = "caddy:2-alpine"
        self.docker("pull", caddy_image)
        self.report["caddy_image"] = json.loads(self.docker("image", "inspect", caddy_image))[0][
            "RepoDigests"
        ]
        self.docker(
            "run",
            "--rm",
            "--network",
            "none",
            "--env",
            "PUBLIC_HOST=pilot.example.org",
            "--env",
            "EDITOR_CIDR=127.0.0.1/32",
            "--mount",
            f"type=bind,src={ROOT / 'deploy' / 'Caddyfile'},dst=/etc/caddy/Caddyfile,readonly",
            caddy_image,
            "caddy",
            "validate",
            "--config",
            "/etc/caddy/Caddyfile",
            "--adapter",
            "caddyfile",
        )
        self.checked("Unmodified production Caddy configuration validates in the real Caddy image")
        # Test routing on an internal-only network. HTTP here intentionally does not claim TLS acceptance.
        caddyfile = directory / "Caddyfile"
        caddyfile.write_text(
            (ROOT / "deploy" / "Caddyfile")
            .read_text(encoding="utf-8")
            .replace("{$PUBLIC_HOST} {", "http://{$PUBLIC_HOST} {", 1),
            encoding="utf-8",
        )
        network = self.prefix + "-private"
        self.docker("network", "create", "--internal", network)
        self.networks.append(network)
        details = self.inspect("network", network)
        ensure(details["Internal"])
        subnet = ipaddress.ip_network(details["IPAM"]["Config"][0]["Subnet"])
        proxy_ip, app_ip = str(subnet.network_address + 2), str(subnet.network_address + 3)
        # Bound only within an internal Docker network with zero host port bindings.
        self.env.update(HOST="0.0.0.0", TRUSTED_PROXY=proxy_ip)  # nosec B104
        self.start("upstream", volume, network, ("--ip", app_ip, "--network-alias", "newsletter"))
        proxy = self.prefix + "-proxy"
        self.containers.append(proxy)
        self.docker(
            "run",
            "--detach",
            "--name",
            proxy,
            "--network",
            network,
            "--ip",
            proxy_ip,
            "--network-alias",
            "proxy",
            "--env",
            "PUBLIC_HOST=pilot.example.org",
            "--env",
            "EDITOR_CIDR=127.0.0.1/32",
            "--security-opt",
            "no-new-privileges:true",
            "--memory",
            "256m",
            "--mount",
            f"type=bind,src={caddyfile},dst=/etc/caddy/Caddyfile,readonly",
            caddy_image,
        )
        ensure(not json.loads(self.docker("inspect", proxy))[0]["HostConfig"]["PortBindings"])
        for attempt in range(20):
            try:
                self.docker(
                    "run",
                    "--rm",
                    "--network",
                    network,
                    self.image,
                    "python",
                    "tools/container_acceptance_probe.py",
                    "proxy",
                )
                break
            except RuntimeError:
                if attempt == 19:
                    raise
                time.sleep(1)
        self.checked(
            "Real Caddy proxy: canonical metadata, public archive, four editor CIDR denials and request limit on isolated network"
        )

    def run(self):
        try:
            if self.docker("info", "--format", "{{.OSType}}") != "linux":
                raise RuntimeError("Acceptance requires a Linux Docker daemon")
            # BuildKit may keep FROM layers in its cache without creating a daemon image
            # entry; pull explicitly so the base digest can be inspected as evidence.
            self.docker("pull", "python:3.12-slim")
            self.docker("build", "--pull", "--tag", self.image, ROOT)
            self.report["image_id"] = json.loads(self.docker("image", "inspect", self.image))[0][
                "Id"
            ]
            self.report["python_base_image"] = json.loads(
                self.docker("image", "inspect", "python:3.12-slim")
            )[0]["RepoDigests"]
            self.checked("Actual Dockerfile builds on Linux")
            with tempfile.TemporaryDirectory(prefix=self.prefix) as temp:
                directory = Path(temp)
                self.compose(directory)
                volume = self.volume("source")
                name = self.start("app", volume)
                self.probe(name, "runtime")
                self.checked(
                    "Non-root image startup, real healthcheck, readonly root, resource limits and no external network"
                )
                self.docker("exec", name, "python", "tools/pilot_smoke.py")
                self.checked(
                    "Authenticated import, approval bypass rejection, review, approval, synthetic publication and public archive"
                )
                self.docker("restart", name)
                self.healthy(name)
                self.docker("exec", name, "python", "tools/pilot_smoke.py", "--verify-existing")
                self.checked("Mounted-volume publication survives actual container restart")
                self.probe(name, "seed")
                expected = self.probe(name, "fingerprint")
                self.docker(
                    "exec",
                    name,
                    "python",
                    "tools/database_backup.py",
                    "backup",
                    "/data/verification.db",
                    "/data/backups/verification.db",
                )
                self.docker(
                    "exec",
                    name,
                    "python",
                    "tools/database_backup.py",
                    "check",
                    "/data/backups/verification.db",
                )
                restored = self.volume("restore")
                self.docker(
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--mount",
                    f"type=volume,src={volume},dst=/source,readonly",
                    "--mount",
                    f"type=volume,src={restored},dst=/data",
                    self.image,
                    "python",
                    "tools/database_backup.py",
                    "restore",
                    "/source/backups/verification.db",
                    "/data/verification.db",
                )
                restore_name = self.start("restored", restored)
                ensure(self.probe(restore_name, "fingerprint") == expected)
                self.docker(
                    "exec",
                    restore_name,
                    "python",
                    "tools/database_backup.py",
                    "restore",
                    "/data/verification.db",
                    "/data/verification.db",
                    expected=1,
                )
                self.docker(
                    "exec",
                    restore_name,
                    "python",
                    "tools/database_backup.py",
                    "restore",
                    "/app/requirements.txt",
                    "/data/rejected.db",
                    expected=1,
                )
                self.checked(
                    "Online backup, integrity, separate-volume restore and invalid/existing restore rejection; consent and delivery ledger preserved"
                )
                self.docker("stop", name, restore_name)
                self.docker(
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--mount",
                    f"type=volume,src={volume},dst=/data",
                    self.image,
                    "python",
                    "-c",
                    "import sqlite3; c=sqlite3.connect('/data/verification.db'); "
                    "c.execute('DROP TABLE rate_limits'); c.execute('PRAGMA user_version=1'); c.commit(); c.close()",
                )
                self.docker("start", name)
                self.healthy(name)
                ensure(self.probe(name, "fingerprint") == expected)
                self.docker("stop", name)
                self.checked(
                    "Actual image migrates v1 SQLite volume to v2 without losing publication, consent or ledger"
                )
                self.proxy(directory, volume)
            self.report["result"] = "PASS"
        finally:
            cleanup_errors = []
            for command in [
                *[("rm", "--force", name) for name in reversed(self.containers)],
                *[("network", "rm", name) for name in self.networks],
                *[("volume", "rm", name) for name in self.volumes],
            ]:
                try:
                    self.docker(*command)
                except (OSError, RuntimeError) as exc:
                    cleanup_errors.append(type(exc).__name__)
            self.report["cleanup_errors"] = cleanup_errors
            if cleanup_errors:
                self.report["result"] = "FAIL"
            self.output.parent.mkdir(parents=True, exist_ok=True)
            self.output.write_text(json.dumps(self.report, indent=2) + "\n", encoding="utf-8")
            if cleanup_errors:
                raise RuntimeError("Disposable container cleanup failed; see runner state")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="signal-daily:acceptance")
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".tmp/container-acceptance/report.json"
    )
    args = parser.parse_args()
    Acceptance(args.image, args.output).run()


if __name__ == "__main__":
    main()
