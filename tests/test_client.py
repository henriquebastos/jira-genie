# Pip imports
import pytest

# Internal imports
from jira.client import IssueSubClient, SearchSubClient

BASE_URL = "https://api.atlassian.com/ex/jira/cloud-abc/"


@pytest.fixture()
def issue(responses):
    from requestspro.sessions import ProSession

    session = ProSession(base_url=BASE_URL)
    return IssueSubClient(session)


@pytest.fixture()
def search(responses):
    from requestspro.sessions import ProSession

    session = ProSession(base_url=BASE_URL)
    return SearchSubClient(session)


class TestIssueSubClient:
    def test_get_calls_correct_url(self, issue, responses):
        responses.add("GET", f"{BASE_URL}rest/api/3/issue/DEV-123", json={"key": "DEV-123"})
        result = issue.get("DEV-123")
        assert result["key"] == "DEV-123"

    def test_get_passes_fields_param(self, issue, responses):
        responses.add("GET", f"{BASE_URL}rest/api/3/issue/DEV-123", json={"key": "DEV-123"})
        issue.get("DEV-123", fields=["summary", "status"])
        req = responses.calls[0].request
        assert "fields=summary%2Cstatus" in req.url

    def test_create_posts_correct_payload(self, issue, responses):
        responses.add("POST", f"{BASE_URL}rest/api/3/issue", json={"key": "DEV-999"})
        result = issue.create({"fields": {"project": {"key": "DEV"}, "summary": "New"}})
        assert result["key"] == "DEV-999"
        assert responses.calls[0].request.body

    def test_edit_puts_to_correct_url(self, issue, responses):
        responses.add("PUT", f"{BASE_URL}rest/api/3/issue/DEV-123", json={})
        issue.edit("DEV-123", {"fields": {"summary": "Updated"}})
        req = responses.calls[0].request
        assert req.method == "PUT"

    def test_delete_sends_delete(self, issue, responses):
        responses.add("DELETE", f"{BASE_URL}rest/api/3/issue/DEV-123", json={})
        issue.delete("DEV-123")
        assert responses.calls[0].request.method == "DELETE"


class TestSearchSubClient:
    def test_jql_posts_search(self, search, responses):
        responses.add("POST", f"{BASE_URL}rest/api/3/search", json={
            "issues": [{"key": "DEV-1"}, {"key": "DEV-2"}],
            "total": 2,
        })
        result = search.jql("project = DEV")
        assert len(result) == 2
        assert result[0]["key"] == "DEV-1"

    def test_jql_all_paginates(self, search, responses):
        responses.add("POST", f"{BASE_URL}rest/api/3/search", json={
            "issues": [{"key": "DEV-1"}],
            "startAt": 0,
            "maxResults": 1,
            "total": 2,
        })
        responses.add("POST", f"{BASE_URL}rest/api/3/search", json={
            "issues": [{"key": "DEV-2"}],
            "startAt": 1,
            "maxResults": 1,
            "total": 2,
        })
        result = search.jql_all("project = DEV")
        assert len(result) == 2
        assert result[0]["key"] == "DEV-1"
        assert result[1]["key"] == "DEV-2"
