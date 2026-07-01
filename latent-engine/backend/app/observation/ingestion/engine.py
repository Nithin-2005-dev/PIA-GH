from __future__ import annotations

from time import perf_counter

from app.observation.ingestion.adapters import AdapterRegistry
from app.observation.ingestion.checkpoint import CheckpointStore
from app.observation.ingestion.dedupe import ObservationDeduplicator
from app.observation.ingestion.metrics import ObservationMetrics
from app.observation.ingestion.models import ReplayQuery
from app.observation.ingestion.models import SyncCursor
from app.observation.ingestion.models import SyncRequest
from app.observation.ingestion.models import SyncResult
from app.observation.ingestion.normalizer import ObservationNormalizer
from app.observation.ingestion.rate_limit import RateLimiter
from app.observation.ingestion.replay import ObservationReplayEngine
from app.observation.ingestion.storage import ObservationIngestionStore
from app.observation.validation import ObservationValidationPipeline
from app.observation.validation import ObservationValidationStatus
from app.platform.event_bus import EventBus
from app.platform.event_bus import PlatformEvent


class ObservationIngestionEngine:
    def __init__(
        self,
        adapters: AdapterRegistry | None = None,
        normalizer: ObservationNormalizer | None = None,
        validator: ObservationValidationPipeline | None = None,
        store: ObservationIngestionStore | None = None,
        checkpoints: CheckpointStore | None = None,
        deduplicator: ObservationDeduplicator | None = None,
        rate_limiter: RateLimiter | None = None,
        event_bus: EventBus | None = None,
        metrics: ObservationMetrics | None = None,
    ):
        self.adapters = adapters or AdapterRegistry()
        self.normalizer = normalizer or ObservationNormalizer()
        self.validator = validator or ObservationValidationPipeline()
        self.store = store or ObservationIngestionStore()
        self.checkpoints = checkpoints or CheckpointStore()
        self.deduplicator = deduplicator or ObservationDeduplicator()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.event_bus = event_bus or EventBus()
        self.metrics = metrics or ObservationMetrics()

    def sync(
        self,
        adapter_name: str,
        request: SyncRequest,
    ) -> SyncResult:
        started = perf_counter()
        if not self.rate_limiter.allow(adapter_name):
            self.rate_limiter.record_failure(adapter_name)
            self.metrics.failures += 1
            return SyncResult(
                adapter=adapter_name,
                raw_count=0,
                normalized_count=0,
                accepted_count=0,
                duplicate_count=0,
                failed_count=1,
                checkpoint=(
                    request.cursor
                    or self.checkpoints.get(adapter_name)
                    or SyncCursor(
                        adapter=adapter_name,
                    )
                ),
            )

        adapter = self.adapters.get(adapter_name)
        effective_request = request
        if effective_request.cursor is None:
            checkpoint = self.checkpoints.get(adapter_name)
            if checkpoint is not None:
                effective_request = SyncRequest(
                    source=request.source,
                    mode=request.mode,
                    cursor=checkpoint,
                    since=request.since,
                    until=request.until,
                    batch_size=request.batch_size,
                    replay=request.replay,
                )

        try:
            raw_records, cursor = adapter.fetch(effective_request)
            self.rate_limiter.record_success(adapter_name)
        except Exception:
            self.rate_limiter.record_failure(adapter_name)
            self.metrics.failures += 1
            raise

        accepted = 0
        normalized = 0
        duplicates = 0
        failed = 0

        for record in raw_records:
            self.metrics.raw_records += 1
            if self.deduplicator.is_duplicate_raw(record):
                duplicates += 1
                self.metrics.duplicates += 1
                continue

            self.store.append_raw(record)
            try:
                observation = self.normalizer.normalize(record)
                normalized += 1
                self.metrics.normalized += 1
            except Exception:
                failed += 1
                self.metrics.failures += 1
                continue

            if self.deduplicator.is_duplicate_observation(observation):
                duplicates += 1
                self.metrics.duplicates += 1
                continue

            validation = self.validator.validate(observation)
            if validation.status == ObservationValidationStatus.FAILED:
                failed += 1
                self.metrics.failures += 1
                continue

            self.store.append_normalized(observation)
            accepted += 1
            self.metrics.accepted += 1
            self.event_bus.publish(
                PlatformEvent(
                    type="observation.normalized",
                    payload=observation,
                    version=observation.version,
                    correlation_id=observation.correlation_id,
                    trace_id=observation.trace_id,
                )
            )

        checkpoint = self.checkpoints.save(cursor)
        self.metrics.backlog = max(
            0,
            len(raw_records) - accepted,
        )
        self.metrics.ingestion_latency_ms += (
            perf_counter() - started
        ) * 1000

        return SyncResult(
            adapter=adapter_name,
            raw_count=len(raw_records),
            normalized_count=normalized,
            accepted_count=accepted,
            duplicate_count=duplicates,
            failed_count=failed,
            checkpoint=checkpoint,
        )

    def replay(
        self,
        query: ReplayQuery | None = None,
    ):
        return ObservationReplayEngine(self.store).replay(query)
