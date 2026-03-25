# Internal imports
from jira.cli import parse


class TestParseAuth:
    def test_auth_login(self):
        args = parse(["auth", "login"])
        assert args.command == "auth"
        assert args.subcommand == "login"

    def test_auth_status(self):
        args = parse(["auth", "status"])
        assert args.command == "auth"
        assert args.subcommand == "status"

    def test_auth_logout(self):
        args = parse(["auth", "logout"])
        assert args.command == "auth"
        assert args.subcommand == "logout"

    def test_instance_flag(self):
        args = parse(["--instance", "acme", "auth", "login"])
        assert args.instance == "acme"
        assert args.command == "auth"
