from __future__ import annotations

from app.observation.domain import Observation
from app.observation.ingestion.models import ReplayQuery
from app.observation.ingestion.storage import ObservationIngestionStore


class ObservationReplayEngine:
    def __init__(
        self,
        store: ObservationIngestionStore,
    ):
        self._store = store

    def replay(
        self,
        query: ReplayQuery | None = None,
    ) -> tuple[Observation, ...]:
        query = query or ReplayQuery()
        results = []
        for observation in self._store.normalized():
            if query.repository and observation.context.repository != query.repository:
                continue
            if query.organization and observation.context.organization != query.organization:
                continue
            if query.adapter and observation.source_adapter != query.adapter:
                continue
            if query.start and observation.timestamp < query.start:
                continue
            if query.end and observation.timestamp > query.end:
                continue
            if query.developer:
                actor_ids = {
                    actor.id
                    for actor in observation.actors
                }
                if query.developer not in actor_ids:
                    continue
            results.append(observation)
        return tuple(results)

