from dataclasses import dataclass
from enum import Enum

from app.measurement.domain import Measurement
from app.measurement.domain import MeasurementDefinition
from app.measurement.domain import MeasurementUnit
from app.measurement.domain import ValidationResult
from app.measurement.domain import ValidationStatus


class MeasurementLifecycle(Enum):
    DRAFT = "draft"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MeasurementContract:
    definition: MeasurementDefinition
    input_signals: tuple[str, ...]
    output_unit: MeasurementUnit
    precision: float | None
    confidence_model: str
    lifecycle: MeasurementLifecycle
    assumptions: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = ()


class MeasurementContractValidator:

    def validate(
        self,
        measurement: Measurement,
        contract: MeasurementContract,
    ) -> ValidationResult:
        errors = []

        if measurement.definition.id != contract.definition.id:
            errors.append(
                "measurement definition does not match contract"
            )

        if measurement.unit != contract.output_unit:
            errors.append(
                "measurement output unit does not match contract"
            )

        if contract.lifecycle in {
            MeasurementLifecycle.DEPRECATED,
            MeasurementLifecycle.ARCHIVED,
        }:
            errors.append(
                "measurement contract is not active"
            )

        if errors:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                checks=("contract",),
                errors=tuple(errors),
            )

        return ValidationResult(
            status=ValidationStatus.PASSED,
            checks=("contract",),
        )


