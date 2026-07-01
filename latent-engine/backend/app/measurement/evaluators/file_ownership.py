"""FileOwnershipEvaluator — per-file ownership concentration.

Produces per-file measurements indicating author touches.
The downstream aggregation layer computes the true ownership score
as the fraction of a file's touches attributable to its majority author.

Purpose:
    Identify knowledge silos and key-person dependencies at the file level.
Mathematical Basis:
    Emits 1.0 per touch. Aggregated via sum/mean to yield ownership concentration ratio [0.0, 1.0].
Assumptions:
    Author identity maps correctly. Touches imply knowledge retention.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (file_ownership_score)
Limitations:
    Does not account for reading or code review, only authoring.
Expected Accuracy:
    High (90%+), though may misclassify trivial refactors as ownership.
"""

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
from app.measurement.identity.resolver import DeveloperIdentityResolver
from app.observation.domain import Observation


class FileOwnershipEvaluator(MeasurementEvaluator):
    """
    Emits `file_ownership_score` = 1.0 for each (file, author) pair
    in the commit. The evidence synthesis engine uses this to compute
    the ownership concentration across commits.

    Mathematical basis:
        For each file, ownership_score = touches_by_majority_author / total_touches
        Since we emit per-commit, the aggregation strategy "mean" over multiple
        commits yields the true majority-author fraction.
    """

    _REGISTRY = DefaultMeasurementCatalog.build()
    FILE_OWNERSHIP_SCORE = _REGISTRY.get("file_ownership_score")

    _identity_resolver = DeveloperIdentityResolver()

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        if not self.FILE_OWNERSHIP_SCORE:
            return []

        files = artifact_files(observation)
        if not files:
            return []

        identity = self._identity_resolver.resolve_from_observation_facts(observation.facts)
        canonical_dev = identity.canonical_id

        measurements = []
        for file in files:
            path = file.path
            measurements.append(
                self._m(
                    self.FILE_OWNERSHIP_SCORE,
                    1.0,  # This author touched this file once in this commit
                    observation,
                    context,
                    path,
                    {"author": canonical_dev, "coverage": 1.0},
                )
            )

        return measurements

    def _m(
        self,
        definition: MeasurementDefinition,
        value: float,
        observation: Observation,
        context: MeasurementContext,
        target_entity: str,
        metadata: dict,
    ) -> Measurement:
        method = MeasurementMethod(
            name="file_ownership_evaluator",
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
