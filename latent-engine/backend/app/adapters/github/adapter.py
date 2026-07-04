from typing import Iterator
from app.adapters.github.gateway import GitHubGateway
from app.observation.adapters.github import GitHubObservationTranslator
from app.observation.domain import Observation
from app.observation.integration import observation_to_event
from app.ports.event_query import EventQuery
from app.ports.event_source_port import ObservationSourcePort
from app.observation.ingestion.resilience import with_resilience


class GitHubAdapter(ObservationSourcePort):
    """
    GitHub source adapter.

    The adapter authenticates and fetches through the gateway, then delegates
    translation to the observation layer. It does not calculate measurements,
    evidence, risk, confidence, or business meaning.
    """

    def __init__(
        self,
        gateway: GitHubGateway,
        translator: GitHubObservationTranslator | None = None,
    ):
        self._gateway = gateway
        self._translator = translator or GitHubObservationTranslator()

    def is_circuit_open(self) -> bool:
        """Check if the underlying gateway's circuit breaker is open."""
        if hasattr(self._gateway, "circuit_breaker"):
            return self._gateway.circuit_breaker.is_open()
        return False

    @with_resilience(max_retries=3, base_delay=1.0)
    def collect(
        self,
        query: EventQuery,
    ) -> Iterator[Observation]:
        owner, repo = query.identifier.split("/")
        raw_commits_generator = self._gateway.fetch_commits(
            query
        )

        for raw_commit in raw_commits_generator:
            sha = raw_commit[
                "sha"
            ]

            details = self._gateway.fetch_commit_details(
                owner=owner,
                repo=repo,
                sha=sha,
            )

            yield self._translator.commit(
                raw_commit,
                details,
                repository=query.identifier,
            )

    def collect_events(
        self,
        query: EventQuery,
    ):
        """
        Deprecated compatibility bridge for legacy scripts.
        """
        return [
            observation_to_event(
                observation
            )
            for observation in self.collect(
                query
            )
        ]
