from abc import ABC, abstractmethod

from app.ports.event_query import EventQuery


class GitHubGateway(ABC):
    """
    Boundary between our system and GitHub.
    """

    @abstractmethod
    def fetch_commits(
        self,
        query: EventQuery,
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_commit_details(
        self,
        owner: str,
        repo: str,
        sha: str,
    ) -> dict:
        raise NotImplementedError