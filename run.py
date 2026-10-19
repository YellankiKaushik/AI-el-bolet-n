"""Load local configuration and start Signal Daily."""

from config import load_env
import ipaddress
import os


def main():
    load_env()
    # Local startup is mail-off unless the operator explicitly configures otherwise.
    os.environ.setdefault("EMAIL_DELIVERY_ENABLED", "false")
    host = os.getenv("HOST", "127.0.0.1")
    if host != "localhost":
        try:
            local = ipaddress.ip_address(host).is_loopback
        except ValueError:
            local = False
        if not local:
            raise ValueError(
                "Local startup requires a loopback HOST; do not expose run.py publicly"
            )
    import server

    server.main()


if __name__ == "__main__":
    main()
