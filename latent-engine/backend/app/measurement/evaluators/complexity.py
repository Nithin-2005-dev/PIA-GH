from app.domain.event import Event

from app.measurement.domain.catalog import DefaultMeasurementCatalog
from app.measurement.domain import Measurement
from app.measurement.domain import MeasurementContext
from app.measurement.domain import MeasurementDefinition
from app.measurement.domain import MeasurementMethod
from app.measurement.domain import MeasurementProvenance
from app.measurement.domain import MeasurementTrace
from app.measurement.domain import MeasurementUncertainty
from app.measurement.domain import MeasurementUnit
from app.measurement.domain import NormalizationMethod
from app.measurement.core.ids import stable_measurement_id
from app.measurement.core.interfaces import MeasurementEvaluator
from app.measurement.evaluators.common import additions
from app.measurement.evaluators.common import artifact_files
from app.measurement.evaluators.common import deletions
from app.measurement.evaluators.common import entropy
from app.measurement.evaluators.common import files_changed


class ChangeComplexityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    CODE_CHURN = _REGISTRY.get("code_churn")

    FILES_CHANGED = _REGISTRY.get("files_changed")

    PATCH_COMPLEXITY_DELTA = _REGISTRY.get(
        "patch_complexity_delta"
    )

    CHANGE_DISTRIBUTION_ENTROPY = _REGISTRY.get(
        "change_distribution_entropy"
    )

    _COMPLEXITY_TOKENS = (
        " if ",
        " for ",
        " while ",
        " case ",
        " catch ",
        " except ",
        "&&",
        "||",
        "?",
    )

    def evaluate(
        self,
        event: Event,
        context: MeasurementContext,
    ) -> list[Measurement]:
        payload = event.payload
        files = artifact_files(
            payload
        )

        churn = additions(
            payload
        ) + deletions(
            payload
        )

        file_count = files_changed(
            payload
        )

        complexity_delta = self._patch_complexity_delta(
            files
        )

        distribution_entropy = entropy(
            [
                float(
                    file.get(
                        "changes",
                        0,
                    )
                    or 0
                )
                for file in files
            ]
        )

        return [
            self._measurement(
                self.CODE_CHURN,
                churn,
                event,
                context,
                {
                    "coverage": 1.0,
                },
            ),
            self._measurement(
                self.FILES_CHANGED,
                file_count,
                event,
                context,
                {
                    "coverage": 1.0 if file_count > 0 else 0.5,
                },
            ),
            self._measurement(
                self.PATCH_COMPLEXITY_DELTA,
                complexity_delta,
                event,
                context,
                {
                    "coverage": self._patch_coverage(
                        files
                    ),
                },
            ),
            self._measurement(
                self.CHANGE_DISTRIBUTION_ENTROPY,
                distribution_entropy,
                event,
                context,
                {
                    "coverage": 1.0 if files else 0.4,
                },
            ),
        ]

    def _measurement(
        self,
        definition: MeasurementDefinition,
        value: float,
        event: Event,
        context: MeasurementContext,
        metadata,
    ) -> Measurement:
        source = str(
            event.metadata.get(
                "source",
                "unknown",
            )
        )

        adapter = str(
            event.metadata.get(
                "gateway",
                "unknown",
            )
        )

        method = MeasurementMethod(
            name="change_complexity_evaluator",
            version="1.0",
            algorithm=definition.id,
        )

        return Measurement(
            id=stable_measurement_id(
                event.id,
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
                source_system=source,
                adapter=adapter,
                source_event_id=str(
                    event.id
                ),
                source_entity_ids=tuple(
                    target.id
                    for target in event.target_refs
                ),
                transformations=(
                    "event.payload.observation",
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

    def _patch_complexity_delta(
        self,
        files,
    ) -> float:
        score = 0.0

        for file in files:
            patch = file.get(
                "patch",
            )

            if not patch:
                continue

            for line in str(
                patch
            ).splitlines():
                if line.startswith(
                    "+++"
                ) or line.startswith(
                    "---"
                ):
                    continue

                sign = 0.0

                if line.startswith(
                    "+"
                ):
                    sign = 1.0
                elif line.startswith(
                    "-"
                ):
                    sign = -1.0

                if sign == 0.0:
                    continue

                normalized = (
                    f" {line[1:].lower()} "
                )

                score += sign * sum(
                    1
                    for token in self._COMPLEXITY_TOKENS
                    if token in normalized
                )

        return score

    def _patch_coverage(
        self,
        files,
    ) -> float:
        if not files:
            return 0.0

        files_with_patch = sum(
            1
            for file in files
            if file.get(
                "patch",
            )
        )

        return files_with_patch / len(
            files
        )



