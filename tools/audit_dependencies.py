"""Query OSV for all pinned packages. Only public package names/versions are sent."""

import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    runtime_count = 0
    pins = []
    for filename in ("requirements.txt", "requirements-dev.txt"):
        entries = [
            line.split("==")
            for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
            if "==" in line and not line.startswith("#")
        ]
        if filename == "requirements.txt":
            runtime_count = len(entries)
        pins.extend(entries)
    queries = [
        {"package": {"name": name, "ecosystem": "PyPI"}, "version": version}
        for name, version in pins
    ]
    request = Request(
        "https://api.osv.dev/v1/querybatch",
        data=json.dumps({"queries": queries}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:  # nosec B310
        result = json.load(response)
    findings = [
        {"package": name, "version": version, "advisories": response.get("vulns", [])}
        for (name, version), response in zip(pins, result["results"], strict=True)
    ]
    report = {
        "source": "https://api.osv.dev/v1/querybatch",
        "runtime_third_party_packages": runtime_count,
        "runtime_packages": findings[:runtime_count],
        "developer_packages": findings[runtime_count:],
        "advisory_count": sum(len(r["advisories"]) for r in findings),
    }
    (ROOT / "docs/dependency-audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"packages_checked": len(pins), "advisory_count": report["advisory_count"]}))
    return bool(report["advisory_count"])


if __name__ == "__main__":
    raise SystemExit(main())
