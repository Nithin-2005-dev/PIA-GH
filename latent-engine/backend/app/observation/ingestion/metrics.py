from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ObservationMetrics:
    raw_records: int = 0
    normalized: int = 0
    accepted: int = 0
    failures: int = 0
    retries: int = 0
    duplicates: int = 0
    ingestion_latency_ms: float = 0.0
    backlog: int = 0

    @property
    def duplicate_rate(
        self,
    ) -> float:
        if self.raw_records == 0:
            return 0.0
        return self.duplicates / self.raw_records

    @property
    def throughput(
        self,
    ) -> float:
        if self.ingestion_latency_ms <= 0:
            return float(self.accepted)
        return self.accepted / (self.ingestion_latency_ms / 1000.0)

