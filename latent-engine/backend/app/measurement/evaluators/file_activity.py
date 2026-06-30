import re
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


class FileActivityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    FILE_CHURN = _REGISTRY.get("file_churn")
    FILE_TOUCH_COUNT = _REGISTRY.get("file_touch_count")
    FILE_ADDITION_RATIO = _REGISTRY.get("file_addition_ratio")
    FILE_IS_TEST = _REGISTRY.get("file_is_test")
    FILE_IS_DOCUMENTATION = _REGISTRY.get("file_is_documentation")

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(observation)
        measurements = []

        for file in files:
            path = file.path
            additions = getattr(file, "additions", 0)
            deletions = getattr(file, "deletions", 0)
            changes = additions + deletions
            
            # File churn
            if self.FILE_CHURN:
                measurements.append(
                    self._measurement(
                        self.FILE_CHURN,
                        float(changes),
                        observation,
                        context,
                        path,
                        {"coverage": 1.0},
                    )
                )

            # Touch count (1 per commit)
            if self.FILE_TOUCH_COUNT:
                measurements.append(
                    self._measurement(
                        self.FILE_TOUCH_COUNT,
                        1.0,
                        observation,
                        context,
                        path,
                        {"coverage": 1.0},
                    )
                )

            # Addition ratio
            if self.FILE_ADDITION_RATIO and changes > 0:
                measurements.append(
                    self._measurement(
                        self.FILE_ADDITION_RATIO,
                        float(additions) / float(changes),
                        observation,
                        context,
                        path,
                        {"coverage": 1.0},
                    )
                )

            # Is test
            if self.FILE_IS_TEST:
                is_test = 1.0 if re.search(r'test|spec|mock|fixture', path, re.IGNORECASE) else 0.0
                measurements.append(
                    self._measurement(
                        self.FILE_IS_TEST,
                        is_test,
                        observation,
                        context,
                        path,
                        {"coverage": 1.0},
                    )
                )

            # Is documentation
            if self.FILE_IS_DOCUMENTATION:
                is_doc = 1.0 if re.search(r'\.md|\.rst|\.txt|docs/|wiki/', path, re.IGNORECASE) else 0.0
                measurements.append(
                    self._measurement(
                        self.FILE_IS_DOCUMENTATION,
                        is_doc,
                        observation,
                        context,
                        path,
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
            name="file_activity_evaluator",
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
                target_entity_type="module",
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
