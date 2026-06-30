from app.measurement.core.ids import stable_measurement_id
from app.measurement.core.interfaces import MeasurementEvaluator
from app.measurement.domain import Measurement
from app.measurement.domain import MeasurementContext
from app.measurement.domain import MeasurementDefinition
from app.measurement.domain import MeasurementMethod
from app.measurement.domain import MeasurementProvenance
from app.measurement.domain import MeasurementTrace
from app.measurement.domain import MeasurementUncertainty
from app.measurement.domain import NormalizationMethod
from app.measurement.domain.catalog import DefaultMeasurementCatalog
from app.measurement.evaluators.common import artifact_files
from app.observation.domain import Observation


class DeveloperActivityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    AUTHOR_CONTRIBUTION_COUNT = _REGISTRY.get("author_contribution_count")
    AUTHOR_FILE_TOUCH_COUNT = _REGISTRY.get("author_file_touch_count")
    AUTHOR_CODE_CHURN = _REGISTRY.get("author_code_churn")

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        if not hasattr(observation.facts, "author_name") or not observation.facts.author_name:
            return []

        author_name = observation.facts.author_name
        files = artifact_files(observation)

        total_churn = 0
        file_touches = len(files)

        for file in files:
            total_churn += getattr(file, "additions", 0) + getattr(file, "deletions", 0)

        measurements = []

        if self.AUTHOR_CONTRIBUTION_COUNT:
            measurements.append(
                self._measurement(
                    self.AUTHOR_CONTRIBUTION_COUNT,
                    1.0,
                    observation,
                    context,
                    author_name,
                    {"coverage": 1.0},
                )
            )

        if self.AUTHOR_FILE_TOUCH_COUNT:
            measurements.append(
                self._measurement(
                    self.AUTHOR_FILE_TOUCH_COUNT,
                    float(file_touches),
                    observation,
                    context,
                    author_name,
                    {"coverage": 1.0 if file_touches > 0 else 0.0},
                )
            )

        if self.AUTHOR_CODE_CHURN:
            measurements.append(
                self._measurement(
                    self.AUTHOR_CODE_CHURN,
                    float(total_churn),
                    observation,
                    context,
                    author_name,
                    {"coverage": 1.0},
                )
            )

        return measurements

    def _measurement(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        target_entity: str,
        metadata: dict,
    ) -> Measurement:
        method = MeasurementMethod(
            name="developer_activity_evaluator",
            version="1.0",
            algorithm=definition.id,
        )

        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                definition.id,
                f"{definition.version}:{target_entity}",
            ),
            definition=definition,
            unit=definition.unit,
            value=value,
            confidence=0.0,
            uncertainty=MeasurementUncertainty(
                lower_bound=value,
                upper_bound=value,
                variance=0.0,
            ),
            quality_score=0.0,
            measurement_method=method,
            normalization_method=NormalizationMethod(
                name="not_normalized",
                version="1.0",
                source_unit=definition.unit,
                target_unit=definition.unit,
            ),
            provenance=MeasurementProvenance(
                source_system=observation.source_platform,
                adapter=observation.source_adapter,
                source_event_id=observation.observation_id,
                source_observation_id=observation.observation_id,
                source_entity_ids=tuple(target.id for target in observation.targets),
                transformations=("observation.facts", method.name),
                tenant_id=context.tenant_id,
                target_entity=target_entity,
                target_entity_type="developer",
                measurement_scope="commit",
            ),
            timestamp=context.timestamp,
            version=definition.version,
            traceability=MeasurementTrace(
                pipeline_version=context.pipeline_version,
                evaluator=method.name,
            ),
            metadata=metadata,
        )
