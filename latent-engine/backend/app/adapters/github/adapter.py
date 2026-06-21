from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.event import Event
from app.domain.event_type import EventType

from app.ports.event_query import EventQuery
from app.ports.event_source_port import EventSourcePort

from app.adapters.github.gateway import GitHubGateway


class GitHubAdapter(EventSourcePort):

    def __init__(
        self,
        gateway: GitHubGateway,
    ):
        self._gateway = gateway

    def collect(
        self,
        query: EventQuery,
    ) -> list[Event]:

        owner, repo = query.identifier.split("/")

        raw_commits = self._gateway.fetch_commits(query)

        events = []

        for raw_commit in raw_commits:

            sha = raw_commit["sha"]

            details = self._gateway.fetch_commit_details(
                owner=owner,
                repo=repo,
                sha=sha,
            )

            events.append(
                self._normalize_commit(
                    raw_commit,
                    details,
                )
            )

        return events

    def _normalize_commit(
        self,
        raw: dict,
        details: dict,
    ) -> Event:

        return Event(
            id=self._event_id(raw),

            type=EventType.COMMIT,

            actor_ref=self._actor(raw),

            target_refs=self._targets(details),

            occurred_at=self._occurred_at(raw),

            payload=self._payload(
                raw,
                details,
            ),

            metadata=self._metadata(),
        )

    def _event_id(
        self,
        raw: dict,
    ):

        sha = raw["sha"]

        return uuid5(
            NAMESPACE_URL,
            sha,
        )

    def _actor(
        self,
        raw: dict,
    ) -> EntityRef:

        author = raw.get("author")

        if author is None:
            return EntityRef(
                id="unknown",
                type=EntityType.DEVELOPER,
            )

        return EntityRef(
            id=author["login"],
            type=EntityType.DEVELOPER,
        )

    def _targets(
        self,
        details: dict,
    ) -> tuple[EntityRef, ...]:

        files = details.get(
            "files",
            [],
        )

        targets = []

        for file in files:

            targets.append(
                EntityRef(
                    id=file["filename"],
                    type=EntityType.FILE,
                )
            )

        return tuple(targets)

    def _occurred_at(
        self,
        raw: dict,
    ) -> datetime:

        timestamp = raw["commit"]["author"]["date"]

        return datetime.fromisoformat(
            timestamp.replace(
                "Z",
                "+00:00",
            )
        )

    def _payload(
        self,
        raw: dict,
        details: dict,
    ) -> dict:

        stats = details.get(
            "stats",
            {},
        )

        return {
            "sha": raw["sha"],
            "message": raw["commit"]["message"],
            "additions": stats.get(
                "additions",
                0,
            ),
            "deletions": stats.get(
                "deletions",
                0,
            ),
            "total_changes": stats.get(
                "total",
                0,
            ),
        }

    def _metadata(
        self,
    ) -> dict:

        return {
            "source": "github",
            "gateway": "rest",
        }