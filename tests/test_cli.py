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


class TestParseFields:
    def test_fields_sync(self):
        args = parse(["fields", "sync"])
        assert args.command == "fields"
        assert args.subcommand == "sync"

    def test_fields_sync_with_project(self):
        args = parse(["fields", "sync", "--project", "DEV"])
        assert args.project == "DEV"

    def test_fields_list(self):
        args = parse(["fields", "list"])
        assert args.command == "fields"
        assert args.subcommand == "list"

    def test_fields_list_with_filter(self):
        args = parse(["fields", "list", "--filter", "team"])
        assert args.filter == "team"

    def test_fields_schema(self):
        args = parse(["fields", "schema", "--project", "DEV", "--type", "Task"])
        assert args.project == "DEV"
        assert args.type == "Task"


class TestParseIssue:
    def test_issue_get(self):
        args = parse(["issue", "get", "DEV-123"])
        assert args.command == "issue"
        assert args.subcommand == "get"
        assert args.key == "DEV-123"

    def test_issue_get_with_fields(self):
        args = parse(["issue", "get", "DEV-123", "--fields", "summary,status"])
        assert args.fields == "summary,status"

    def test_issue_get_raw(self):
        args = parse(["issue", "get", "DEV-123", "--raw"])
        assert args.raw is True

    def test_issue_edit_with_set(self):
        args = parse(["issue", "edit", "DEV-123", "--set", "parent=DEV-100", "--set", "priority=P1"])
        assert args.set == ["parent=DEV-100", "priority=P1"]

    def test_issue_edit_with_json(self):
        args = parse(["issue", "edit", "DEV-123", "--json", '{"team": "Backend"}'])
        assert args.json == '{"team": "Backend"}'

    def test_issue_edit_raw(self):
        args = parse(["issue", "edit", "DEV-123", "--raw-payload", '{"fields": {}}'])
        assert args.raw_payload == '{"fields": {}}'

    def test_search(self):
        args = parse(["search", "project = DEV AND status != Done"])
        assert args.command == "search"
        assert args.jql == "project = DEV AND status != Done"

    def test_search_with_fields(self):
        args = parse(["search", "project = DEV", "--fields", "summary,status"])
        assert args.fields == "summary,status"

    def test_bulk_edit(self):
        args = parse(["bulk", "edit", "DEV-1", "DEV-2", "--set", "parent=DEV-100"])
        assert args.command == "bulk"
        assert args.keys == ["DEV-1", "DEV-2"]
        assert args.set == ["parent=DEV-100"]
