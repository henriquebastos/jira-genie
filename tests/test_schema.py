# Python imports
import json

# Internal imports
from jira.schema import build_field_registry, build_type_schema, friendly_name, resolve_fields, sync


class TestFriendlyName:
    def test_converts_display_name(self):
        assert friendly_name("Story Points") == "story_points"

    def test_handles_single_word(self):
        assert friendly_name("Summary") == "summary"

    def test_handles_already_lowercase(self):
        assert friendly_name("status") == "status"

    def test_handles_extra_spaces(self):
        assert friendly_name("Epic  Link") == "epic_link"


RAW_FIELDS = [
    {"id": "summary", "name": "Summary", "schema": {"type": "string"}, "custom": False},
    {"id": "status", "name": "Status", "schema": {"type": "status"}, "custom": False},
    {"id": "customfield_10036", "name": "Story Points", "schema": {"type": "number"}, "custom": True},
    {"id": "customfield_10001", "name": "Team", "schema": {"type": "option"}, "custom": True},
]


class TestBuildFieldRegistry:
    def test_maps_fields_to_friendly_names(self):
        registry = build_field_registry(RAW_FIELDS)
        assert "summary" in registry
        assert "story_points" in registry
        assert registry["story_points"]["id"] == "customfield_10036"
        assert registry["story_points"]["type"] == "number"

    def test_system_fields_keep_native_ids(self):
        registry = build_field_registry(RAW_FIELDS)
        assert registry["summary"]["id"] == "summary"
        assert registry["summary"]["system"] is True

    def test_custom_fields_marked_not_system(self):
        registry = build_field_registry(RAW_FIELDS)
        assert registry["story_points"].get("system") is not True
        assert registry["story_points"]["name"] == "Story Points"


RAW_CREATEMETA = {
    "id": "10002",
    "name": "Task",
    "fields": {
        "summary": {"required": True, "schema": {"type": "string"}, "name": "Summary"},
        "priority": {
            "required": False,
            "schema": {"type": "priority"},
            "name": "Priority",
            "allowedValues": [{"name": "P0: Critical"}, {"name": "P1: High"}],
        },
        "customfield_10036": {
            "required": False,
            "schema": {"type": "number"},
            "name": "Story Points",
        },
    },
}


class TestBuildTypeSchema:
    def test_extracts_required_fields(self):
        schema = build_type_schema(RAW_CREATEMETA)
        assert schema["id"] == "10002"
        assert "summary" in schema["required"]

    def test_extracts_field_types_and_allowed_values(self):
        schema = build_type_schema(RAW_CREATEMETA)
        assert schema["fields"]["priority"]["type"] == "priority"
        assert schema["fields"]["priority"]["allowed"] == ["P0: Critical", "P1: High"]
        assert schema["fields"]["priority"]["required"] is False

    def test_fields_without_allowed_values(self):
        schema = build_type_schema(RAW_CREATEMETA)
        assert "allowed" not in schema["fields"]["customfield_10036"]


SCHEMA_FIELDS = {
    "summary": {"id": "summary", "type": "string", "system": True},
    "status": {"id": "status", "type": "status", "system": True},
    "parent": {"id": "parent", "type": "issuelink", "system": True},
    "priority": {"id": "priority", "type": "priority", "system": True},
    "labels": {"id": "labels", "type": "array", "system": True},
    "story_points": {"id": "customfield_10036", "type": "number", "name": "Story Points"},
    "team": {"id": "customfield_10001", "type": "option", "name": "Team"},
    "components": {"id": "components", "type": "array", "system": True},
}


class TestResolveFields:
    def test_string_passthrough(self):
        result = resolve_fields({"summary": "Fix bug"}, SCHEMA_FIELDS)
        assert result == {"summary": "Fix bug"}

    def test_name_resolution(self):
        result = resolve_fields({"story_points": 5}, SCHEMA_FIELDS)
        assert result == {"customfield_10036": 5}

    def test_issuelink_expansion(self):
        result = resolve_fields({"parent": "DEV-123"}, SCHEMA_FIELDS)
        assert result == {"parent": {"key": "DEV-123"}}

    def test_system_option_expansion(self):
        result = resolve_fields({"priority": "P1: High"}, SCHEMA_FIELDS)
        assert result == {"priority": {"name": "P1: High"}}

    def test_custom_option_expansion(self):
        result = resolve_fields({"team": "Backend"}, SCHEMA_FIELDS)
        assert result == {"customfield_10001": {"value": "Backend"}}

    def test_labels_passthrough(self):
        result = resolve_fields({"labels": ["urgent"]}, SCHEMA_FIELDS)
        assert result == {"labels": ["urgent"]}

    def test_unknown_field_passthrough(self):
        result = resolve_fields({"unknown_field": "value"}, SCHEMA_FIELDS)
        assert result == {"unknown_field": "value"}

    def test_already_structured_passthrough(self):
        result = resolve_fields({"parent": {"key": "DEV-123"}}, SCHEMA_FIELDS)
        assert result == {"parent": {"key": "DEV-123"}}

    def test_multiple_fields(self):
        result = resolve_fields({"summary": "Fix", "story_points": 3, "team": "Backend"}, SCHEMA_FIELDS)
        assert result == {"summary": "Fix", "customfield_10036": 3, "customfield_10001": {"value": "Backend"}}


class TestSync:
    def test_writes_schema_json(self, tmp_path, responses):
        # Mock the field list endpoint
        responses.add("GET", "https://api.atlassian.com/ex/jira/cloud-abc/rest/api/3/field", json=RAW_FIELDS)

        # Mock createmeta endpoints
        responses.add(
            "GET",
            "https://api.atlassian.com/ex/jira/cloud-abc/rest/api/3/issue/createmeta/DEV/issuetypes",
            json={"issueTypes": [{"id": "10002", "name": "Task"}]},
        )
        responses.add(
            "GET",
            "https://api.atlassian.com/ex/jira/cloud-abc/rest/api/3/issue/createmeta/DEV/issuetypes/10002",
            json=RAW_CREATEMETA,
        )

        instance_dir = tmp_path / "cloud-abc"
        instance_dir.mkdir()
        (instance_dir / "config.json").write_text(json.dumps({
            "cloud_id": "cloud-abc",
            "site": "acme.atlassian.net",
        }))

        from requestspro.sessions import ProSession

        session = ProSession(base_url="https://api.atlassian.com/ex/jira/cloud-abc/")
        sync(session, instance_dir, project="DEV")

        schema = json.loads((instance_dir / "schema.json").read_text())
        assert "fields" in schema
        assert "projects" in schema
        assert "DEV" in schema["projects"]
        assert schema["synced_at"] is not None
