from dataclasses import replace

from .domain import Measurement
from .domain import MeasurementContext
from .domain import ValidationResult
from .domain import ValidationStatus
from .interfaces import QualityScorer


class DefaultQualityScorer(QualityScorer):

    def score(
        self,
        measurement: Measurement,
        validation: ValidationResult,
        context: MeasurementContext,
    ) -> Measurement:
        validation_score = 1.0

        if validation.status == ValidationStatus.WARNING:
            validation_score = 0.75
        elif validation.status == ValidationStatus.FAILED:
            validation_score = 0.0

        interval_width = (
            measurement.uncertainty.upper_bound
            - measurement.uncertainty.lower_bound
        )

        scale = max(
            abs(
                measurement.value
            ),
            1.0,
        )

        uncertainty_score = max(
            0.0,
            1.0 - min(
                1.0,
                interval_width / (2.0 * scale),
            ),
        )

        quality = (
            0.45 * measurement.confidence
            + 0.30 * uncertainty_score
            + 0.25 * validation_score
        )

        quality = max(
            0.0,
            min(
                1.0,
                quality,
            ),
        )

        return replace(
            measurement,
            quality_score=quality,
            validation_status=validation.status,
            traceability=replace(
                measurement.traceability,
                validator_ids=validation.checks,
            ),
        )
