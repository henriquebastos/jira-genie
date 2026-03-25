# Python imports
import argparse
import json


def parse(argv=None):
    """Pure parsing. Returns a Namespace. No I/O."""
    parser = argparse.ArgumentParser(prog="jira", description="Jira Cloud CLI")
    parser.add_argument("--instance", help="Jira instance (site name)")

    subparsers = parser.add_subparsers(dest="command")

    # auth subcommands
    auth_parser = subparsers.add_parser("auth")
    auth_sub = auth_parser.add_subparsers(dest="subcommand")
    auth_sub.add_parser("login")
    auth_sub.add_parser("status")
    auth_sub.add_parser("logout")

    return parser.parse_args(argv)


def cli(argv=None):
    """Entry point. Parses, dispatches, handles I/O."""
    args = parse(argv)

    if args.command == "auth":
        if args.subcommand == "login":
            print(json.dumps({"message": "Login flow not yet wired"}))
        elif args.subcommand == "status":
            print(json.dumps({"status": "not logged in"}))
        elif args.subcommand == "logout":
            print(json.dumps({"message": "Logged out"}))
    elif args.command is None:
        parse(["--help"])
