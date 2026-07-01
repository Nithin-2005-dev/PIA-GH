from __future__ import annotations

from app.observation.domain import Observation
from app.observation.ingestion.models import RawObservationRecord


class ObservationDeduplicator:
    def __init__(
        self,
    ):
        self._raw_keys: set[tuple[str, str, str]] = set()
        self._observation_ids: set[str] = set()

    def is_duplicate_raw(
        self,
        record: RawObservationRecord,
    ) -> bool:
        key = (
            record.source.provider,
            record.record_type,
            record.record_id,
        )
        if key in self._raw_keys:
            return True
        self._raw_keys.add(key)
        return False

    def is_duplicate_observation(
        self,
        observation: Observation,
    ) -> bool:
        if observation.observation_id in self._observation_ids:
            return True
        self._observation_ids.add(
            observation.observation_id
        )
        return False

