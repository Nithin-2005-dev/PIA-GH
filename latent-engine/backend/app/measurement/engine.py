from dataclasses import replace
from datetime import UTC, datetime

from app.domain.event import Event

from .confidence import DefaultConfidenceEstimator
from .domain import Measurement
from .domain import MeasurementContext
from .domain import ValidationStatus
from .evaluators.complexity import ChangeComplexityEvaluator
from .evaluators.impact import ChangeImpactEvaluator
from .interfaces import ConfidenceEstimator
from .interfaces import MeasurementEvaluator
from .interfaces import MeasurementNormalizer
from .interfaces import MeasurementValidator
from .interfaces import QualityScorer
from .normalization import BoundedScoreNormalizer
from .normalization import IdentityNormalizer
from .normalization import UnitConversionNormalizer
from .normalization_pipeline import NormalizationPipeline
from .quality import DefaultQualityScorer
from .validation import FiniteValueValidator
from .validation import RangeValidator
from .validation import UnitValidator
from .validation import merge_validation_results


class MeasurementEngine:
    """
    Deterministic measurement pipeline.

    The engine consumes immutable events containing observations and
    produces immutable, normalized, validated measurements.
    """

    def __init__(
        self,
        evaluators: list[MeasurementEvaluator],
        normalizers: list[MeasurementNormalizer],
        validators: list[MeasurementValidator],
        confidence_estimator: ConfidenceEstimator,
        quality_scorer: QualityScorer,
        normalization_pipeline: NormalizationPipeline | None = None,
    ):
        self._evaluators = evaluators
        self._normalizers = normalizers
        self._validators = validators
        self._confidence_estimator = confidence_estimator
        self._quality_scorer = quality_scorer
        self._normalization_pipeline = (
            normalization_pipeline
            or NormalizationPipeline.default()
        )

    @classmethod
    def default(
        cls,
    ):
        return cls(
            evaluators=[
                ChangeComplexityEvaluator(),
                ChangeImpactEvaluator(),
            ],
            normalizers=[
                UnitConversionNormalizer(),
                BoundedScoreNormalizer(),
                IdentityNormalizer(),
            ],
            validators=[
                FiniteValueValidator(),
                UnitValidator(),
                RangeValidator(),
            ],
            confidence_estimator=DefaultConfidenceEstimator(),
            quality_scorer=DefaultQualityScorer(),
            normalization_pipeline=NormalizationPipeline.default(),
        )

    def measure_event(
        self,
        event: Event,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        if context is None:
            context = MeasurementContext(
                timestamp=datetime.now(
                    UTC,
                )
            )

        measurements = []

        for evaluator in self._evaluators:
            for measurement in evaluator.evaluate(
                event,
                context,
            ):
                measurements.append(
                    self._finalize(
                        measurement,
                        context,
                    )
                )

        return measurements

    def measure_events(
        self,
        events: list[Event],
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        measurements = []

        for event in events:
            measurements.extend(
                self.measure_event(
                    event,
                    context,
                )
            )

        return measurements

    def _finalize(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        pipeline_measurement, stage_names = (
            self._normalization_pipeline.apply(
                measurement
            )
        )

        normalized = self._normalize(
            replace(
                pipeline_measurement,
                provenance=replace(
                    pipeline_measurement.provenance,
                    transformations=(
                        *pipeline_measurement
                        .provenance
                        .transformations,
                        *stage_names,
                    ),
                ),
            )
        )

        validation = merge_validation_results(
            [
                validator.validate(
                    normalized
                )
                for validator in self._validators
            ]
        )

        with_validation = replace(
            normalized,
            validation_status=validation.status,
        )

        if validation.status == ValidationStatus.FAILED:
            return self._quality_scorer.score(
                with_validation,
                validation,
                context,
            )

        with_confidence = (
            self._confidence_estimator
            .estimate(
                with_validation,
                context,
            )
        )

        return self._quality_scorer.score(
            with_confidence,
            validation,
            context,
        )

    def _normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        for normalizer in self._normalizers:
            if normalizer.supports(
                measurement
            ):
                normalized = normalizer.normalize(
                    measurement
                )

                return replace(
                    normalized,
                    traceability=replace(
                        normalized.traceability,
                        normalizer=(
                            normalized
                            .normalization_method
                            .name
                        ),
                    ),
                )

        return measurement
