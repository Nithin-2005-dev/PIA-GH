from dataclasses import dataclass

from app.evidence.domain import Evidence
from app.evidence.ontology import EvidenceRelationship


@dataclass(frozen=True)
class EvidenceGraphNode:
    id: str
    type: str
    label: str


@dataclass(frozen=True)
class EvidenceGraphEdge:
    source_id: str
    target_id: str
    relationship: EvidenceRelationship


class EvidenceKnowledgeGraph:

    def __init__(
        self,
    ):
        self._nodes: dict[str, EvidenceGraphNode] = {}
        self._edges: list[EvidenceGraphEdge] = []

    def add_evidence(
        self,
        evidence: Evidence,
    ) -> None:
        self._nodes[
            evidence.evidence_id
        ] = EvidenceGraphNode(
            id=evidence.evidence_id,
            type="evidence",
            label=evidence.name,
        )

        for measurement in evidence.supporting_measurements:
            self._nodes[
                measurement.id
            ] = EvidenceGraphNode(
                id=measurement.id,
                type="measurement",
                label=measurement.name,
            )
            self._edges.append(
                EvidenceGraphEdge(
                    source_id=measurement.id,
                    target_id=evidence.evidence_id,
                    relationship=EvidenceRelationship.SUPPORTS,
                )
            )

        concept_id = f"expertise:{evidence.category}"
        self._nodes[
            concept_id
        ] = EvidenceGraphNode(
            id=concept_id,
            type="expertise_concept",
            label=evidence.category,
        )
        self._edges.append(
            EvidenceGraphEdge(
                source_id=evidence.evidence_id,
                target_id=concept_id,
                relationship=EvidenceRelationship.EXPLAINS,
            )
        )

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: EvidenceRelationship,
    ) -> None:
        self._edges.append(
            EvidenceGraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship=relationship,
            )
        )

    def nodes(
        self,
    ) -> tuple[EvidenceGraphNode, ...]:
        return tuple(
            self._nodes.values()
        )

    def edges(
        self,
    ) -> tuple[EvidenceGraphEdge, ...]:
        return tuple(
            self._edges
        )

    def neighbors(
        self,
        node_id: str,
    ) -> tuple[EvidenceGraphNode, ...]:
        ids = {
            edge.target_id
            for edge in self._edges
            if edge.source_id == node_id
        }.union(
            {
                edge.source_id
                for edge in self._edges
                if edge.target_id == node_id
            }
        )
        return tuple(
            self._nodes[
                item_id
            ]
            for item_id in ids
            if item_id in self._nodes
        )

    def lineage(
        self,
        evidence_id: str,
    ) -> tuple[EvidenceGraphEdge, ...]:
        return tuple(
            edge
            for edge in self._edges
            if edge.target_id == evidence_id
            or edge.source_id == evidence_id
        )

    def impact_analysis(
        self,
        measurement_id: str,
    ) -> tuple[EvidenceGraphNode, ...]:
        impacted_ids = {
            edge.target_id
            for edge in self._edges
            if edge.source_id == measurement_id
        }
        return tuple(
            self._nodes[
                node_id
            ]
            for node_id in impacted_ids
            if node_id in self._nodes
        )

