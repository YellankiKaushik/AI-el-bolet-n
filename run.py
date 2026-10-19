"""Load local configuration and start Signal Daily."""

from config import load_env


def main():
    load_env()
    import server

    server.main()


if __name__ == "__main__":
    main()
