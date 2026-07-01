from __future__ import annotations

from app.domain.expertise_estimate import ExpertiseEstimate
from app.evidence.core import EvidencePackage
from app.graph.graph_edge import GraphEdge
from app.graph.graph_node import GraphNode
from app.graph.organizational_graph import OrganizationalGraph


class KnowledgeGraphBuilder:
    def build(
        self,
        expertise_estimates: tuple[ExpertiseEstimate, ...] = (),
        evidence_package: EvidencePackage | None = None,
    ) -> OrganizationalGraph:
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        for estimate in expertise_estimates:
            developer_id = estimate.developer_ref.id
            module_id = estimate.module_ref.id
            nodes[developer_id] = GraphNode(
                id=developer_id,
                type=estimate.developer_ref.type.value,
            )
            nodes[module_id] = GraphNode(
                id=module_id,
                type=estimate.module_ref.type.value,
            )
            edges.append(
                GraphEdge(
                    source_id=developer_id,
                    target_id=module_id,
                    relationship="HAS_EXPERTISE_IN",
                    weight=estimate.raw_score,
                )
            )

        if evidence_package is not None:
            for evidence in evidence_package.evidence:
                evidence_id = f"evidence:{evidence.evidence_id}"
                target_id = evidence.metadata.get("target_entity")
                if not target_id or target_id == "global":
                    continue
                nodes[evidence_id] = GraphNode(
                    id=evidence_id,
                    type="EVIDENCE",
                )
                nodes.setdefault(
                    str(target_id),
                    GraphNode(
                        id=str(target_id),
                        type=str(
                            evidence.metadata.get(
                                "target_entity_type",
                                "UNKNOWN",
                            )
                        ),
                    ),
                )
                edges.append(
                    GraphEdge(
                        source_id=evidence_id,
                        target_id=str(target_id),
                        relationship="SUPPORTS",
                        weight=evidence.confidence,
                    )
                )
                for measurement in evidence.supporting_measurements:
                    measurement_id = f"measurement:{measurement.id}"
                    nodes[measurement_id] = GraphNode(
                        id=measurement_id,
                        type="MEASUREMENT",
                    )
                    edges.append(
                        GraphEdge(
                            source_id=measurement_id,
                            target_id=evidence_id,
                            relationship="SYNTHESIZES_TO",
                            weight=measurement.confidence,
                        )
                    )

        return OrganizationalGraph(
            nodes=list(nodes.values()),
            edges=edges,
        )

