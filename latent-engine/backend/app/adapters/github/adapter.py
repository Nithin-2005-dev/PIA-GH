from app.adapters.github.gateway import GitHubGateway
from app.observation.adapters.github import GitHubObservationTranslator
from app.observation.domain import Observation
from app.observation.integration import observation_to_event
from app.ports.event_query import EventQuery
from app.ports.event_source_port import ObservationSourcePort


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

    def collect(
        self,
        query: EventQuery,
    ) -> list[Observation]:
        owner, repo = query.identifier.split("/")
        raw_commits = self._gateway.fetch_commits(
            query
        )

        observations = []

        for raw_commit in raw_commits:
            sha = raw_commit[
                "sha"
            ]

            details = self._gateway.fetch_commit_details(
                owner=owner,
                repo=repo,
                sha=sha,
            )

            observations.append(
                self._translator.commit(
                    raw_commit,
                    details,
                    repository=query.identifier,
                )
            )

        return observations

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
