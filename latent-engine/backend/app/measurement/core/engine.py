from dataclasses import replace
from datetime import UTC, datetime

from app.measurement.core.confidence import DefaultConfidenceEstimator
from app.measurement.domain import Measurement
from app.measurement.domain import MeasurementContext
from app.measurement.domain import ValidationStatus
from app.measurement.evaluators.complexity import ChangeComplexityEvaluator
from app.measurement.evaluators.impact import ChangeImpactEvaluator
from app.measurement.evaluators.developer_activity import DeveloperActivityEvaluator
from app.measurement.evaluators.file_activity import FileActivityEvaluator
from app.measurement.evaluators.file_ownership import FileOwnershipEvaluator
from app.measurement.evaluators.subsystem_activity import SubsystemActivityEvaluator
from app.measurement.core.interfaces import ConfidenceEstimator
from app.measurement.core.interfaces import MeasurementEvaluator
from app.measurement.core.interfaces import MeasurementNormalizer
from app.measurement.core.interfaces import MeasurementValidator
from app.measurement.core.interfaces import QualityScorer
from app.measurement.core.normalization import BoundedScoreNormalizer
from app.measurement.core.normalization import IdentityNormalizer
from app.measurement.core.normalization import UnitConversionNormalizer
from app.measurement.core.normalization_pipeline import NormalizationPipeline
from app.measurement.core.quality import DefaultQualityScorer
from app.measurement.core.validation import FiniteValueValidator
from app.measurement.core.validation import RangeValidator
from app.measurement.core.validation import UnitValidator
from app.measurement.core.validation import merge_validation_results
from app.observation.domain import Observation
from app.observation.integration.event_compat import event_to_observation


class MeasurementEngine:
    """
    Deterministic measurement pipeline.

    The engine consumes immutable canonical observations and
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
                DeveloperActivityEvaluator(),
                FileActivityEvaluator(),
                SubsystemActivityEvaluator(),
                FileOwnershipEvaluator(),
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

    def measure_observation(
        self,
        observation: Observation,
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
                observation,
                context,
            ):
                measurements.append(
                    self._finalize(
                        measurement,
                        context,
                    )
                )

        return measurements

    def measure_observations(
        self,
        observations: list[Observation],
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        measurements = []

        for observation in observations:
            measurements.extend(
                self.measure_observation(
                    observation,
                    context,
                )
            )

        # Increment 1: Perform mathematical calibration over the measurement population
        from app.measurement.core.calibration.engine import StatisticalCalibrationEngine
        calibration_engine = StatisticalCalibrationEngine()
        return list(calibration_engine.calibrate(measurements))

    def measure_event(
        self,
        event,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        """
        Deprecated compatibility bridge.

        Measurement's canonical contract is `Observation`. Legacy callers that
        still hold `app.domain.event.Event` are translated before evaluation.
        """
        return self.measure_observation(
            event_to_observation(event),
            context,
        )

    def measure_events(
        self,
        events: list,
        context: MeasurementContext | None = None,
    ) -> list[Measurement]:
        return self.measure_observations(
            [
                event_to_observation(event)
                for event in events
            ],
            context,
        )

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


