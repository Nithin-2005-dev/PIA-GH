import requests
from typing import Iterator

from app.ports.event_query import EventQuery

from app.adapters.github.gateway import GitHubGateway


class GitHubRestGateway(GitHubGateway):

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        secret_provider,
        secret_key: str = "GITHUB_TOKEN"
    ):
        from app.observation.ingestion.circuit_breaker import CircuitBreaker
        self.secret_provider = secret_provider
        self.secret_key = secret_key
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout_sec=60.0)

    def _get_headers(self) -> dict:
        token = self.secret_provider.get_secret(self.secret_key)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    def _handle_rate_limit(self, response: requests.Response):
        import time
        import logging
        logger = logging.getLogger(__name__)
        
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        
        if remaining is not None and int(remaining) == 0 and reset is not None:
            reset_time = int(reset)
            current_time = int(time.time())
            sleep_time = max(0, reset_time - current_time)
            if sleep_time > 0:
                logger.warning(f"GitHub Rate Limit Exceeded. Blocking execution for {sleep_time} seconds until reset.")
                time.sleep(sleep_time)

    def _make_request(self, url: str, params: dict = None) -> dict:
        def fetch():
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params or {},
                timeout=30,
            )
            self._handle_rate_limit(response)
            response.raise_for_status()
            return response.json()
            
        return self.circuit_breaker.call(fetch)

    def fetch_commits(
        self,
        query: EventQuery,
    ) -> Iterator[dict]:

        owner, repo = query.identifier.split("/")

        url = (
            f"{self.BASE_URL}"
            f"/repos/{owner}/{repo}/commits"
        )

        params = dict(query.filters) if query.filters else {}
        params["per_page"] = 100
        page = 1
        
        while True:
            params["page"] = page
            page_data = self._make_request(url, params=params)
            
            if not page_data:
                break
                
            for item in page_data:
                yield item
                
            if len(page_data) < 100:
                break
            page += 1

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

        return self._make_request(url)