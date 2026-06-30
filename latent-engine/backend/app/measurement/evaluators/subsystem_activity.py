from collections import defaultdict
import os
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


class SubsystemActivityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    DIRECTORY_CHURN = _REGISTRY.get("directory_churn")
    DIRECTORY_FILE_COUNT = _REGISTRY.get("directory_file_count")

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(observation)
        measurements = []
        
        dir_churn = defaultdict(int)
        dir_files = defaultdict(set)

        for file in files:
            directory = os.path.dirname(file.path)
            if not directory:
                directory = "/"
            
            changes = getattr(file, "additions", 0) + getattr(file, "deletions", 0)
            dir_churn[directory] += changes
            dir_files[directory].add(file.path)

        for directory, churn in dir_churn.items():
            if self.DIRECTORY_CHURN:
                measurements.append(
                    self._measurement(
                        self.DIRECTORY_CHURN,
                        float(churn),
                        observation,
                        context,
                        directory,
                        {"coverage": 1.0},
                    )
                )

        for directory, file_set in dir_files.items():
            if self.DIRECTORY_FILE_COUNT:
                measurements.append(
                    self._measurement(
                        self.DIRECTORY_FILE_COUNT,
                        float(len(file_set)),
                        observation,
                        context,
                        directory,
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
            name="subsystem_activity_evaluator",
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
                target_entity_type="subsystem",
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
