from math import log1p

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
from app.measurement.evaluators.common import additions
from app.measurement.evaluators.common import artifact_files
from app.measurement.evaluators.common import deletions
from app.measurement.evaluators.common import files_changed
from app.measurement.evaluators.common import total_changes
from app.observation.domain import Observation


class ChangeImpactEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    CHANGE_SURFACE_AREA = _REGISTRY.get("change_surface_area")
    REVIEW_ATTENTION_NEED = _REGISTRY.get("review_attention_need")

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(
            observation
        )

        churn = total_changes(
            observation
        )

        file_count = files_changed(
            observation
        )

        surface_area = min(
            100.0,
            log1p(
                max(
                    churn,
                    0.0,
                )
            )
            * max(
                1.0,
                file_count,
            )
            * 4.0,
        )

        deletion_ratio = 0.0

        line_total = additions(
            observation
        ) + deletions(
            observation
        )

        if line_total > 0:
            deletion_ratio = deletions(
                observation
            ) / line_total

        patch_coverage = self._patch_coverage(
            files
        )

        attention = min(
            100.0,
            surface_area
            * 0.65
            + deletion_ratio * 20.0
            + (1.0 - patch_coverage) * 15.0,
        )

        return [
            self._measurement(
                self.CHANGE_SURFACE_AREA,
                surface_area,
                observation,
                context,
                {
                    "coverage": 1.0 if churn > 0 else 0.4,
                },
            ),
            self._measurement(
                self.REVIEW_ATTENTION_NEED,
                attention,
                observation,
                context,
                {
                    "coverage": max(
                        0.35,
                        patch_coverage,
                    ),
                    "missing_penalty": (
                        1.0 - patch_coverage
                    )
                    * 0.25,
                },
            ),
        ]

    def _measurement(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        metadata,
    ) -> Measurement:
        method = MeasurementMethod(
            name="change_impact_evaluator",
            version="1.0",
            algorithm=definition.id,
        )

        return Measurement(
            id=stable_measurement_id(
                observation.observation_id,
                definition.id,
                definition.version,
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
                source_entity_ids=tuple(
                    target.id
                    for target in observation.targets
                ),
                transformations=(
                    "observation.facts",
                    method.name,
                ),
                tenant_id=context.tenant_id,
            ),
            timestamp=context.timestamp,
            version=definition.version,
            traceability=MeasurementTrace(
                pipeline_version=context.pipeline_version,
                evaluator=method.name,
            ),
            metadata=metadata,
        )

    def _patch_coverage(
        self,
        files,
    ) -> float:
        if not files:
            return 0.0

        files_with_patch = sum(
            1
            for file in files
            if file.patch
        )

        return files_with_patch / len(
            files
        )
