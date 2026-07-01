"""Stage 07b - Knowledge Graph via the canonical graph service."""

from __future__ import annotations

from app.graph.builders import KnowledgeGraphBuilder

from ..context import PlatformContext
from ..ui import metric, section, success, warning
from .base import PipelineStage


class KnowledgeGraphStage(PipelineStage):
    name = "Knowledge Graph Construction"

    def execute(
        self,
        context: PlatformContext,
    ) -> None:
        knowledge_models = getattr(context, "knowledge", [])
        expertise_models = getattr(context, "expertise_models", [])
        evidence_package = getattr(context, "evidence_package", None)

        if not knowledge_models and not expertise_models:
            warning("No knowledge or expertise models - skipping Knowledge Graph")
            return

        builder = context.resolve(KnowledgeGraphBuilder)
        graph = builder.build_from_models(
            knowledge_models=knowledge_models,
            expertise_models=expertise_models,
            evidence_package=evidence_package,
        )

        context.knowledge_graph = graph
        context.metrics["graph_nodes"] = len(graph.nodes)
        context.metrics["graph_edges"] = len(graph.edges)

        section("Knowledge Graph")
        metric("Nodes", len(graph.nodes))
        metric("Edges", len(graph.edges))
        success("Knowledge Graph constructed by canonical Graph Service")
