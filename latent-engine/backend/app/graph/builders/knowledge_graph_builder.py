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

    def build_from_models(
        self,
        knowledge_models,
        expertise_models,
        evidence_package: EvidencePackage | None = None,
    ) -> OrganizationalGraph:
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        for model in knowledge_models:
            nodes[model.id] = GraphNode(
                id=model.id,
                type="knowledge",
                attributes={
                    "entity_type": model.entity_type,
                    "topic": model.topic,
                    "score": model.average_score,
                    "confidence": model.average_confidence,
                },
            )

        for model in expertise_models:
            entity_type = (
                "subsystem"
                if model.category == "module"
                else model.category
            )
            nodes[model.id] = GraphNode(
                id=model.id,
                type="expertise",
                attributes={
                    "subject": model.subject,
                    "category": model.category,
                    "entity_type": entity_type,
                    "score": model.score,
                    "confidence": model.confidence,
                },
            )
            for evidence_id in model.evidence_ids:
                nodes.setdefault(
                    evidence_id,
                    GraphNode(
                        id=evidence_id,
                        type="evidence",
                    ),
                )
                edges.append(
                    GraphEdge(
                        source_id=evidence_id,
                        target_id=model.id,
                        relationship="SUPPORTS_EXPERTISE",
                        weight=model.confidence,
                    )
                )

        if evidence_package is not None:
            for evidence in evidence_package.evidence:
                evidence_id = str(evidence.evidence_id)
                nodes.setdefault(
                    evidence_id,
                    GraphNode(
                        id=evidence_id,
                        type="evidence",
                        attributes={
                            "name": evidence.name,
                            "confidence": evidence.confidence,
                        },
                    ),
                )
                for measurement_id in evidence.lineage.source_measurement_ids:
                    nodes.setdefault(
                        measurement_id,
                        GraphNode(
                            id=measurement_id,
                            type="measurement",
                        ),
                    )
                    edges.append(
                        GraphEdge(
                            source_id=measurement_id,
                            target_id=evidence_id,
                            relationship="SUPPORTS_EVIDENCE",
                            weight=evidence.confidence,
                        )
                    )

        knowledge_nodes = [
            node
            for node in nodes.values()
            if node.type == "knowledge"
        ]
        for model in expertise_models:
            entity_type = (
                "subsystem"
                if model.category == "module"
                else model.category
            )
            for node in knowledge_nodes:
                attributes = node.attributes or {}
                if (
                    attributes.get("entity_type") == entity_type
                    and attributes.get("topic") == model.subject
                ):
                    edges.append(
                        GraphEdge(
                            source_id=model.id,
                            target_id=node.id,
                            relationship="SUPPORTS_KNOWLEDGE",
                            weight=model.confidence,
                        )
                    )

        return OrganizationalGraph(
            nodes=list(nodes.values()),
            edges=edges,
        )
