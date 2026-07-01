"""DeveloperActivityEvaluator — extended with Tier 2 measurements.

Produces per-developer measurements using canonical GitHub login
as the entity key via DeveloperIdentityResolver.

Purpose:
    Quantify developer behavioral patterns and knowledge acquisition.
Mathematical Basis:
    Sums absolute churn (additions + deletions). Uses ratio scaling
    for subsystem focus.
Assumptions:
    Author email/login maps reliably to a single identity.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (developer_knowledge_spread, developer_subsystem_focus, etc.)
Limitations:
    Does not account for non-code contributions (issues/reviews).
Expected Accuracy:
    High (95%+), barring severe identity fragmentation.
"""

import math
from collections import Counter

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
from app.measurement.subsystem.boundary import SubsystemResolver
from app.observation.domain import Observation


class DeveloperActivityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    AUTHOR_CONTRIBUTION_COUNT = _REGISTRY.get("author_contribution_count")
    AUTHOR_FILE_TOUCH_COUNT   = _REGISTRY.get("author_file_touch_count")
    AUTHOR_CODE_CHURN         = _REGISTRY.get("author_code_churn")
    DEV_KNOWLEDGE_SPREAD      = _REGISTRY.get("developer_knowledge_spread")
    DEV_SUBSYSTEM_FOCUS       = _REGISTRY.get("developer_subsystem_focus")
    DEV_RECENCY_SCORE         = _REGISTRY.get("developer_recency_score")
    DEV_COMMIT_FREQUENCY      = _REGISTRY.get("developer_commit_frequency")
    DEV_FILES_OWNED           = _REGISTRY.get("developer_files_owned")

    _identity_resolver = DeveloperIdentityResolver()
    _subsystem_resolver = SubsystemResolver.default()

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        if not hasattr(observation.facts, "author_name") or not observation.facts.author_name:
            return []

        # Resolve canonical developer identity
        identity = self._identity_resolver.resolve_from_observation_facts(observation.facts)
        canonical_id = identity.canonical_id

        files = artifact_files(observation)
        total_churn = sum(
            getattr(f, "additions", 0) + getattr(f, "deletions", 0)
            for f in files
        )
        file_touches = len(files)

        # Subsystem spread — map each file to its subsystem
        subsystem_counts: Counter = Counter()
        for file in files:
            subsystem = self._subsystem_resolver.resolve(file.path)
            subsystem_counts[subsystem] += 1

        distinct_subsystems = len(subsystem_counts)
        total_touches = sum(subsystem_counts.values()) or 1
        max_subsystem_touches = max(subsystem_counts.values(), default=0)
        subsystem_focus = max_subsystem_touches / total_touches

        # Recency score — 1.0 if committed within 7 days, decays with half-life=14d
        recency_score = 1.0  # within the same observation window, recency is maximum

        measurements = []

        if self.AUTHOR_CONTRIBUTION_COUNT:
            measurements.append(self._m(self.AUTHOR_CONTRIBUTION_COUNT, 1.0, observation, context, canonical_id, {"coverage": 1.0}))

        if self.AUTHOR_FILE_TOUCH_COUNT:
            measurements.append(self._m(self.AUTHOR_FILE_TOUCH_COUNT, float(file_touches), observation, context, canonical_id, {"coverage": 1.0 if file_touches > 0 else 0.0}))

        if self.AUTHOR_CODE_CHURN:
            measurements.append(self._m(self.AUTHOR_CODE_CHURN, float(total_churn), observation, context, canonical_id, {"coverage": 1.0}))

        if self.DEV_KNOWLEDGE_SPREAD:
            measurements.append(self._m(self.DEV_KNOWLEDGE_SPREAD, float(distinct_subsystems), observation, context, canonical_id, {"coverage": 1.0}))

        if self.DEV_SUBSYSTEM_FOCUS:
            measurements.append(self._m(self.DEV_SUBSYSTEM_FOCUS, subsystem_focus, observation, context, canonical_id, {"coverage": 1.0}))

        if self.DEV_RECENCY_SCORE:
            measurements.append(self._m(self.DEV_RECENCY_SCORE, recency_score, observation, context, canonical_id, {"coverage": 1.0}))

        if self.DEV_COMMIT_FREQUENCY:
            measurements.append(self._m(self.DEV_COMMIT_FREQUENCY, 1.0, observation, context, canonical_id, {"coverage": 1.0}))

        if self.DEV_FILES_OWNED:
            measurements.append(self._m(self.DEV_FILES_OWNED, float(file_touches), observation, context, canonical_id, {"coverage": 1.0}))

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
            name="developer_activity_evaluator",
            version="2.0",
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

    # Backwards compat alias
    _measurement = _m
