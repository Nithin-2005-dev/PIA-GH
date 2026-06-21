import requests

from app.ports.event_query import EventQuery

from app.adapters.github.gateway import GitHubGateway


class GitHubRestGateway(GitHubGateway):

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str,
    ):
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    def fetch_commits(
        self,
        query: EventQuery,
    ) -> list[dict]:

        owner, repo = query.identifier.split("/")

        url = (
            f"{self.BASE_URL}"
            f"/repos/{owner}/{repo}/commits"
        )

        response = requests.get(
            url,
            headers=self._headers,
            params=dict(query.filters),
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def fetch_commit_details(
        self,
        owner: str,
        repo: str,
        sha: str,
    ) -> dict:

        url = (
            f"{self.BASE_URL}"
            f"/repos/{owner}/{repo}/commits/{sha}"
        )

        response = requests.get(
            url,
            headers=self._headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()