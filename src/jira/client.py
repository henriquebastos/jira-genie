# Internal imports
from requestspro.client import Client, MainClient
from requestspro.sessions import ProSession


class JiraSession(ProSession):
    pass


class IssueSubClient(Client):
    def get(self, issue_key, fields=None, expand=None):
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = expand
        return super().get(url=f"rest/api/3/issue/{issue_key}", params=params or None)

    def create(self, payload):
        return self.post(url="rest/api/3/issue", json=payload)

    def edit(self, issue_key, payload):
        return self.put(url=f"rest/api/3/issue/{issue_key}", json=payload)

    def delete(self, issue_key):
        return super().delete(url=f"rest/api/3/issue/{issue_key}")


class SearchSubClient(Client):
    def jql(self, query, fields=None, max_results=50):
        payload = {"jql": query, "maxResults": max_results}
        if fields:
            payload["fields"] = fields
        result = self.post(url="rest/api/3/search", json=payload)
        return result.get("issues", [])

    def jql_all(self, query, fields=None):
        all_issues = []
        start_at = 0
        while True:
            payload = {"jql": query, "startAt": start_at, "maxResults": 50}
            if fields:
                payload["fields"] = fields
            result = self.post(url="rest/api/3/search", json=payload)
            issues = result.get("issues", [])
            all_issues.extend(issues)
            if start_at + len(issues) >= result.get("total", 0):
                break
            start_at += len(issues)
        return all_issues


class JiraClient(MainClient):
    def __init__(self, session):
        super().__init__(session, audit=False)
        self.issue = IssueSubClient(session)
        self.search = SearchSubClient(session)
