"""Thin presentation wrapper for the canonical Platform Runtime."""

from __future__ import annotations

from app.platform import PlatformRuntime

from .config import load_config
from .ui import banner, stage, summary


class PlatformPipeline:
    def __init__(
        self,
    ):
        self.config = load_config()
        self.runtime = PlatformRuntime.create()

    def run(
        self,
    ):
        banner()

        progress = {
            "index": 0,
            "total": 14,
        }

        def show_progress(event):
            progress["index"] += 1
            stage(
                progress["index"],
                progress["total"],
                event.payload["stage"],
            )

        self.runtime.event_bus.subscribe(
            "runtime.stage.started",
            show_progress,
        )

        result = self.runtime.run(
            repository=self.config.repository,
            branch=self.config.branch,
            commits=self.config.commit_limit,
            github_token=self.config.github_token,
            tenant_id=self.config.tenant_id,
            output_directory=self.config.output_directory,
        )

        context = result.context
        org = context.org_intelligence
        package = context.evidence_package
        summary(
            "CANONICAL RUNTIME COMPLETE",
            [
                ("Repository", context.repository),
                ("Branch", context.branch),
                ("Observations", len(context.observations)),
                ("Measurements", len(context.measurements)),
                (
                    "Evidence",
                    len(package.evidence) if package else 0,
                ),
                ("Expertise Models", len(context.expertise_models)),
                ("Knowledge Models", len(context.knowledge)),
                ("Graph Nodes", context.metrics.get("graph_nodes", 0)),
                (
                    "Org Intel - Ownership",
                    len(org.ownership) if org else "N/A",
                ),
                (
                    "Org Intel - Health",
                    f"{org.health.average_health:.3f}" if org else "N/A",
                ),
                ("Reasoning Results", len(context.reasoning_results)),
                ("Decisions", len(context.decisions)),
                ("Runtime Stages", len(result.completed_stages)),
                ("Runtime Errors", len(result.errors)),
            ],
        )

        if result.errors:
            raise RuntimeError("; ".join(result.errors))

        return result
