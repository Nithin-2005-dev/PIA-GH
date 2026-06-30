from dataclasses import dataclass
from enum import Enum

from app.evidence.domain import Evidence
from app.evidence.ontology import EvidenceOntology
from app.evidence.ontology import EvidenceRelationship


class EvidenceCorrelationType(Enum):
    SEMANTIC = "semantic"
    STATISTICAL = "statistical"
    GRAPH = "graph"
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"
    BENCHMARK = "benchmark"
    HISTORICAL = "historical"


@dataclass(frozen=True)
class EvidenceCorrelation:
    source_evidence_id: str
    target_evidence_id: str
    correlation_type: EvidenceCorrelationType
    relationship: EvidenceRelationship
    strength: float
    explanation: str
    implies_causation: bool = False


class EvidenceCorrelationEngine:

    def __init__(
        self,
        ontology: EvidenceOntology,
    ):
        self._ontology = ontology

    def correlate(
        self,
        evidence: tuple[Evidence, ...],
    ) -> tuple[EvidenceCorrelation, ...]:
        correlations = []

        for index, source in enumerate(
            evidence
        ):
            for target in evidence[
                index + 1:
            ]:
                correlations.extend(
                    self._correlate_pair(
                        source,
                        target,
                    )
                )

        return tuple(
            correlations
        )

    def _correlate_pair(
        self,
        source: Evidence,
        target: Evidence,
    ) -> tuple[EvidenceCorrelation, ...]:
        correlations = []

        if source.category == target.category:
            correlations.append(
                EvidenceCorrelation(
                    source_evidence_id=source.evidence_id,
                    target_evidence_id=target.evidence_id,
                    correlation_type=EvidenceCorrelationType.SEMANTIC,
                    relationship=EvidenceRelationship.RELATED_TO,
                    strength=min(
                        source.confidence,
                        target.confidence,
                    ),
                    explanation=(
                        "Evidence items share an ontology category. "
                        "This is correlation, not causation."
                    ),
                )
            )

        source_measurements = set(
            source.lineage.source_measurement_ids
        )
        target_measurements = set(
            target.lineage.source_measurement_ids
        )
        overlap = source_measurements.intersection(
            target_measurements
        )
        if overlap:
            correlations.append(
                EvidenceCorrelation(
                    source_evidence_id=source.evidence_id,
                    target_evidence_id=target.evidence_id,
                    correlation_type=EvidenceCorrelationType.DEPENDENCY,
                    relationship=EvidenceRelationship.DERIVED_FROM,
                    strength=min(
                        1.0,
                        len(
                            overlap
                        )
                        / max(
                            1,
                            len(
                                source_measurements.union(
                                    target_measurements
                                )
                            ),
                        ),
                    ),
                    explanation=(
                        "Evidence items share source measurements. "
                        "Shared provenance does not imply causation."
                    ),
                )
            )

        for edge in self._ontology.relationships_from(
            source.category
        ):
            if edge.target_id == target.category:
                correlations.append(
                    EvidenceCorrelation(
                        source_evidence_id=source.evidence_id,
                        target_evidence_id=target.evidence_id,
                        correlation_type=EvidenceCorrelationType.GRAPH,
                        relationship=edge.relationship,
                        strength=edge.confidence,
                        explanation=(
                            edge.explanation
                            or "Ontology graph relates these concepts."
                        ),
                    )
                )

        return tuple(
            correlations
        )

