from collections.abc import Callable
from dataclasses import dataclass

from app.domain.event import Event

from app.measurement.domain import Measurement
from app.measurement.domain import MeasurementContext
from app.measurement.core.engine import MeasurementEngine


@dataclass(frozen=True)
class MeasurementUpdate:
    event_id: str
    measurements: tuple[Measurement, ...]


class StreamingMeasurementEngine:

    def __init__(
        self,
        engine: MeasurementEngine,
    ):
        self._engine = engine
        self._subscribers: list[
            Callable[[MeasurementUpdate], None]
        ] = []

    def subscribe(
        self,
        subscriber: Callable[[MeasurementUpdate], None],
    ):
        self._subscribers.append(
            subscriber
        )

    def ingest(
        self,
        event: Event,
        context: MeasurementContext,
    ) -> MeasurementUpdate:
        measurements = tuple(
            self._engine.measure_event(
                event,
                context,
            )
        )

        update = MeasurementUpdate(
            event_id=str(
                event.id
            ),
            measurements=measurements,
        )

        for subscriber in self._subscribers:
            subscriber(
                update
            )

        return update


