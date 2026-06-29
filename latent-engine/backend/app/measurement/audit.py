from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MeasurementAuditRecord:
    measurement_id: str
    action: str
    actor: str
    occurred_at: datetime
    details: dict


class MeasurementAuditLog:

    def __init__(
        self,
    ):
        self._records = []

    def append(
        self,
        record: MeasurementAuditRecord,
    ):
        self._records.append(
            record
        )

    def records_for(
        self,
        measurement_id: str,
    ) -> list[MeasurementAuditRecord]:
        return [
            record
            for record in self._records
            if record.measurement_id == measurement_id
        ]
