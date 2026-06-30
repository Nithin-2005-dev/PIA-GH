"""Stage 13 — Executive Intelligence Report (Summary)."""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import metric, ranking, section, success
from .base import PipelineStage


class SummaryStage(PipelineStage):
    name = "Executive Intelligence Report"

    def execute(self, context: PlatformContext) -> None:
        package = context.evidence_package
        health  = context.metrics.get("canonical_health", {})
        org     = context.org_intelligence

        section("Executive Intelligence Report")

        # Pipeline layer counts
        metric("Repository",         context.repository)
        metric("Branch",             context.branch)
        metric("Observations",       len(context.observations))
        metric("Measurements",       len(context.measurements))
        metric("Evidence",           len(package.evidence) if package else 0)
        metric("Evidence for Expertise", len(package.for_expertise()) if package else 0)
        metric("Expertise Models",   len(context.expertise_models))
        metric("Knowledge Models",   len(context.knowledge))
        metric("Reasoning Results",  len(context.reasoning_results))
        metric("Decisions",          len(context.decisions))
        metric(
            "Canonical Health",
            "PASS" if health and all(health.values()) else "PARTIAL" if health else "FAIL",
        )

        # Organization intelligence summary
        if org:
            section("Organization Intelligence Totals")
            metric("Ownership Entries",   len(org.ownership))
            metric("Coverage Entries",    len(org.coverage))
            metric("Concentration Entries", len(org.concentration))
            metric("Bus Factor Entries",  len(org.bus_factors))
            metric("Successor Pairs",     len(org.successors))
            metric("Knowledge Risks",     len(org.knowledge_risks))
            metric("Health (average)",    f"{org.health.average_health:.3f}")
            metric("Healthy Topics",      org.health.healthy_count)
            metric("Warning Topics",      org.health.warning_count)
            metric("Critical Topics",     org.health.critical_count)
            metric("Forecast",            "UNAVAILABLE (single snapshot)")
            metric("Recommendations",     len(org.recommendations))

            # Validation matrix pass / fail summary
            exact   = sum(1 for v in org.validation_matrix if v.match_quality == "EXACT")
            close   = sum(1 for v in org.validation_matrix if v.match_quality == "CLOSE")
            unavail = sum(1 for v in org.validation_matrix if v.match_quality == "UNAVAILABLE")
            metric("Validation Matrix — EXACT match",       exact)
            metric("Validation Matrix — CLOSE match",       close)
            metric("Validation Matrix — UNAVAILABLE",       unavail)

        ranking(
            "Recommended Decisions",
            [
                (
                    f"{d.priority:<8} {d.action:<60} "
                    f"(confidence={d.confidence:.3f})"
                )
                for d in context.decisions
            ],
        )

        if org and org.recommendations:
            ranking(
                "Top Organizational Recommendations",
                [
                    f"[{r.action_type.upper():<14}] [{r.priority.upper():<6}] {r.action[:70]}"
                    for r in org.recommendations[:8]
                ],
            )

        section("Execution Timings")
        for name, timing in context.timings.items():
            metric(name, f"{timing.duration:.3f}s")

        success("Canonical showcase completed")
