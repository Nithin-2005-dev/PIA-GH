from __future__ import annotations

from typing import Protocol

from app.observation.ingestion.models import RawObservationRecord
from app.observation.ingestion.models import SyncRequest
from app.observation.ingestion.models import SyncCursor


class ObservationAdapter(Protocol):
    name: str
    provider: str
    supported_record_types: tuple[str, ...]

    def fetch(
        self,
        request: SyncRequest,
    ) -> tuple[RawObservationRecord, SyncCursor]:
        ...


class AdapterRegistry:
    def __init__(
        self,
    ):
        self._adapters: dict[str, ObservationAdapter] = {}

    def register(
        self,
        adapter: ObservationAdapter,
    ) -> None:
        self._adapters[adapter.name] = adapter

    def get(
        self,
        name: str,
    ) -> ObservationAdapter:
        return self._adapters[name]

    def all(
        self,
    ) -> tuple[ObservationAdapter, ...]:
        return tuple(self._adapters.values())

    def providers(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    adapter.provider
                    for adapter in self._adapters.values()
                }
            )
        )


class StaticObservationAdapter:
    def __init__(
        self,
        name: str,
        provider: str,
        records: tuple[RawObservationRecord, ...] = (),
        supported_record_types: tuple[str, ...] = (),
    ):
        self.name = name
        self.provider = provider
        self._records = records
        self.supported_record_types = supported_record_types

    def fetch(
        self,
        request: SyncRequest,
    ) -> tuple[RawObservationRecord, SyncCursor]:
        offset = (
            request.cursor.offset
            if request.cursor is not None
            else 0
        )
        batch = self._records[
            offset : offset + request.batch_size
        ]
        next_offset = offset + len(batch)
        cursor = (
            batch[-1].cursor
            if batch
            else (
                request.cursor.cursor
                if request.cursor is not None
                else None
            )
        )
        return (
            tuple(batch),
            SyncCursor(
                adapter=self.name,
                cursor=cursor,
                offset=next_offset,
            ),
        )


def default_adapter_names(
) -> tuple[str, ...]:
    return (
        "github",
        "gitlab",
        "bitbucket",
        "jira",
        "linear",
        "azure_devops",
        "slack",
        "teams",
        "email",
        "ci_cd",
        "kubernetes",
        "docker",
        "custom_api",
    )

