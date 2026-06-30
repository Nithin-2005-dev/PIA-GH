"""Stage 07b — Knowledge Graph.

Constructs a Knowledge Graph from Knowledge models, Expertise models, Evidence,
and Measurements to represent the full semantic topology.
"""

from __future__ import annotations

from typing import Any
import networkx as nx

from ..context import PlatformContext
from ..ui import metric, section, success, warning
from .base import PipelineStage


class KnowledgeGraphStage(PipelineStage):
    name = "Knowledge Graph Construction"

    def execute(self, context: PlatformContext) -> None:
        knowledge_models = getattr(context, "knowledge", [])
        expertise_models = getattr(context, "expertise_models", [])
        evidence_package = getattr(context, "evidence_package", None)

        if not knowledge_models and not expertise_models:
            warning("No knowledge or expertise models — skipping Knowledge Graph")
            return

        graph = nx.MultiDiGraph()

        # Add Knowledge nodes
        for k_model in knowledge_models:
            graph.add_node(
                k_model.id,
                type="knowledge",
                topic=k_model.topic,
                score=k_model.average_score,
                confidence=k_model.average_confidence,
            )

        # Add Expertise nodes
        for e_model in expertise_models:
            graph.add_node(
                e_model.id,
                type="expertise",
                subject=e_model.subject,
                category=e_model.category,
                score=e_model.score,
                confidence=e_model.confidence,
            )
            # Link Expertise to Knowledge
            # Assuming Knowledge topic == Expertise subject
            k_id = f"knowledge|{e_model.category}|{e_model.subject}"
            for node in graph.nodes(data=True):
                if node[1].get("type") == "knowledge" and node[1].get("topic") == e_model.subject:
                    graph.add_edge(e_model.id, node[0], relation="supports_knowledge")

            # Link Evidence to Expertise
            for ev_id in e_model.evidence_ids:
                if not graph.has_node(ev_id):
                    graph.add_node(ev_id, type="evidence")
                graph.add_edge(ev_id, e_model.id, relation="supports_expertise")

        if evidence_package:
            for item in evidence_package.evidence:
                if not graph.has_node(item.evidence_id):
                    graph.add_node(
                        item.evidence_id,
                        type="evidence",
                        name=item.name,
                        confidence=item.confidence,
                    )
                for meas_id in item.provenance.measurement_ids:
                    if not graph.has_node(meas_id):
                        graph.add_node(meas_id, type="measurement")
                    graph.add_edge(meas_id, item.evidence_id, relation="supports_evidence")

        context.knowledge_graph = graph
        context.metrics["graph_nodes"] = graph.number_of_nodes()
        context.metrics["graph_edges"] = graph.number_of_edges()

        section("Knowledge Graph")
        metric("Nodes", graph.number_of_nodes())
        metric("Edges", graph.number_of_edges())
        success("Knowledge Graph constructed")
