"""SubsystemActivityEvaluator — extended with Tier 2 measurements.

Uses SubsystemResolver to map file paths to canonical subsystem names.
Produces per-subsystem measurements covering churn, contributors,
file concentration, coupling, and volatility.

Purpose:
    Assess structural risk, knowledge distribution, and volatility at the subsystem level.
Mathematical Basis:
    Gini coefficient for file concentration. Simple sums and ratios for coupling/churn.
Assumptions:
    SubsystemResolver accurately groups files into logical architecture domains.
Inputs:
    Observation (Commits)
Outputs:
    Measurements (subsystem_churn_rate, subsystem_file_concentration, etc.)
Limitations:
    Coupling score is currently bound to single-commit co-changes.
Expected Accuracy:
    High for churn and contributors; moderate for coupling due to single-commit constraint.
"""

import math
from collections import defaultdict
from typing import Any

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


def _gini(values: list[float]) -> float:
    """Compute the Gini coefficient of a list of non-negative values."""
    if not values or sum(values) == 0:
        return 0.0
    n = len(values)
    sorted_vals = sorted(values)
    cumulative = sum((i + 1) * v for i, v in enumerate(sorted_vals))
    total = sum(sorted_vals)
    return (2 * cumulative) / (n * total) - (n + 1) / n


class SubsystemActivityEvaluator(MeasurementEvaluator):

    _REGISTRY = DefaultMeasurementCatalog.build()

    DIRECTORY_CHURN         = _REGISTRY.get("directory_churn")
    DIRECTORY_FILE_COUNT    = _REGISTRY.get("directory_file_count")
    SUBSYSTEM_CHURN_RATE    = _REGISTRY.get("subsystem_churn_rate")
    SUBSYSTEM_CONTRIBUTOR   = _REGISTRY.get("subsystem_contributor_count")
    SUBSYSTEM_CONCENTRATION = _REGISTRY.get("subsystem_file_concentration")
    SUBSYSTEM_COUPLING      = _REGISTRY.get("subsystem_coupling_score")
    SUBSYSTEM_VOLATILITY    = _REGISTRY.get("subsystem_volatility")

    _subsystem_resolver = SubsystemResolver.default()
    _identity_resolver  = DeveloperIdentityResolver()

    def evaluate(
        self,
        observation: Observation,
        context: MeasurementContext,
    ) -> list[Measurement]:
        files = artifact_files(observation)
        measurements = []

        # Resolve developer canonical id for contributor tracking
        identity = self._identity_resolver.resolve_from_observation_facts(observation.facts)
        canonical_dev = identity.canonical_id

        # Group files by canonical subsystem name (not raw directory)
        subsystem_churn:   defaultdict[str, int]        = defaultdict(int)
        subsystem_files:   defaultdict[str, set]        = defaultdict(set)
        subsystem_file_churn: defaultdict[str, list]    = defaultdict(list)

        for file in files:
            subsystem = self._subsystem_resolver.resolve(file.path)
            changes = getattr(file, "additions", 0) + getattr(file, "deletions", 0)
            subsystem_churn[subsystem]  += changes
            subsystem_files[subsystem].add(file.path)
            subsystem_file_churn[subsystem].append(float(changes))

        all_subsystems = set(subsystem_churn) | set(subsystem_files)

        for subsystem in all_subsystems:
            churn      = float(subsystem_churn.get(subsystem, 0))
            file_set   = subsystem_files.get(subsystem, set())
            file_churn = subsystem_file_churn.get(subsystem, [])
            file_count = float(len(file_set))

            # Legacy directory_churn (kept for backwards compat)
            if self.DIRECTORY_CHURN:
                measurements.append(self._m(self.DIRECTORY_CHURN, churn, observation, context, subsystem, {"coverage": 1.0}))

            # Legacy directory_file_count
            if self.DIRECTORY_FILE_COUNT:
                measurements.append(self._m(self.DIRECTORY_FILE_COUNT, file_count, observation, context, subsystem, {"coverage": 1.0}))

            # Tier 2: subsystem_churn_rate
            if self.SUBSYSTEM_CHURN_RATE:
                measurements.append(self._m(self.SUBSYSTEM_CHURN_RATE, churn, observation, context, subsystem, {"coverage": 1.0}))

            # Tier 2: subsystem_contributor_count (1 per commit — aggregated upstream)
            if self.SUBSYSTEM_CONTRIBUTOR:
                measurements.append(self._m(
                    self.SUBSYSTEM_CONTRIBUTOR, 1.0, observation, context, subsystem,
                    {"coverage": 1.0, "developer": canonical_dev},
                ))

            # Tier 2: subsystem_file_concentration (Gini coefficient)
            if self.SUBSYSTEM_CONCENTRATION and file_churn:
                gini = _gini(file_churn)
                measurements.append(self._m(self.SUBSYSTEM_CONCENTRATION, gini, observation, context, subsystem, {"coverage": 1.0}))

            # Tier 2: subsystem_coupling_score
            # Within a single commit, all files in the subsystem are coupled.
            # Score = files_in_subsystem / total_files_in_commit (normalized 0-1)
            if self.SUBSYSTEM_COUPLING:
                total_files_in_commit = len(files) or 1
                coupling = min(file_count / total_files_in_commit, 1.0)
                measurements.append(self._m(self.SUBSYSTEM_COUPLING, coupling, observation, context, subsystem, {"coverage": 1.0}))

            # Tier 2: subsystem_volatility (std dev approximation per commit = |churn|)
            # Proper std dev needs aggregation across commits — we emit the raw churn
            # and let the aggregation layer compute variance.
            if self.SUBSYSTEM_VOLATILITY:
                measurements.append(self._m(self.SUBSYSTEM_VOLATILITY, churn, observation, context, subsystem, {"coverage": 1.0}))

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
            name="subsystem_activity_evaluator",
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

    # Backwards compat alias
    _measurement = _m
