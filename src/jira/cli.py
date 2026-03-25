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

    # fields subcommands
    fields_parser = subparsers.add_parser("fields")
    fields_sub = fields_parser.add_subparsers(dest="subcommand")

    fields_sync = fields_sub.add_parser("sync")
    fields_sync.add_argument("--project", help="Sync specific project")

    fields_list = fields_sub.add_parser("list")
    fields_list.add_argument("--filter", help="Filter fields by name")

    fields_schema = fields_sub.add_parser("schema")
    fields_schema.add_argument("--project", required=True, help="Project key")
    fields_schema.add_argument("--type", required=True, help="Issue type name")

    # issue subcommands
    issue_parser = subparsers.add_parser("issue")
    issue_sub = issue_parser.add_subparsers(dest="subcommand")

    issue_get = issue_sub.add_parser("get")
    issue_get.add_argument("key", help="Issue key (e.g. DEV-123)")
    issue_get.add_argument("--fields", help="Comma-separated field list")
    issue_get.add_argument("--raw", action="store_true", help="Output raw API response")

    issue_edit = issue_sub.add_parser("edit")
    issue_edit.add_argument("key", help="Issue key")
    issue_edit.add_argument("--set", action="append", help="key=value field")
    issue_edit.add_argument("--json", help="JSON override string")
    issue_edit.add_argument("--raw-payload", help="Raw JSON payload (bypass resolution)")

    issue_create = issue_sub.add_parser("create")
    issue_create.add_argument("--summary", help="Issue summary")
    issue_create.add_argument("--template", help="Template name")
    issue_create.add_argument("--json", help="JSON override string")
    issue_create.add_argument("--set", action="append", help="key=value field")
    issue_create.add_argument("--raw-payload", help="Raw JSON payload (bypass resolution)")

    issue_transition = issue_sub.add_parser("transition")
    issue_transition.add_argument("key", help="Issue key")
    issue_transition.add_argument("status", help="Target status name")

    issue_assign = issue_sub.add_parser("assign")
    issue_assign.add_argument("key", help="Issue key")
    issue_assign.add_argument("assignee", help="Email or account ID")

    issue_comment = issue_sub.add_parser("comment")
    issue_comment.add_argument("key", help="Issue key")
    issue_comment.add_argument("body", help="Comment text")

    issue_link = issue_sub.add_parser("link")
    issue_link.add_argument("inward_key", help="Inward issue key")
    issue_link.add_argument("outward_key", help="Outward issue key")
    issue_link.add_argument("--type", dest="link_type", default="blocks", help="Link type")

    # search command
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("jql", help="JQL query string")
    search_parser.add_argument("--fields", help="Comma-separated field list")

    # bulk subcommands
    bulk_parser = subparsers.add_parser("bulk")
    bulk_sub = bulk_parser.add_subparsers(dest="subcommand")

    bulk_edit = bulk_sub.add_parser("edit")
    bulk_edit.add_argument("keys", nargs="+", help="Issue keys")
    bulk_edit.add_argument("--set", action="append", help="key=value field")

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
