"""Stage 11 — Executive Dashboard.

Consumes decisions AND org_intelligence to render a rich executive view.
"""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import lineage, metric, ranking, section, success, warning
from .base import PipelineStage


class ExecutiveDashboardStage(PipelineStage):
    name = "Executive Dashboard"

    def execute(self, context: PlatformContext) -> None:
        if not context.decisions:
            warning("No decisions available")
            return

        section("Executive Dashboard")
        package = context.evidence_package
        metric("Observations",       len(context.observations))
        metric("Measurements",       len(context.measurements))
        metric("Evidence",           len(package.evidence) if package else 0)
        metric("Expertise Models",   len(context.expertise_models))
        metric("Knowledge Models",   len(context.knowledge))
        metric("Reasoning Results",  len(context.reasoning_results))
        metric("Decisions",          len(context.decisions))

        high_priority   = sum(1 for d in context.decisions if d.priority == "high")
        medium_priority = sum(1 for d in context.decisions if d.priority == "medium")
        low_priority    = sum(1 for d in context.decisions if d.priority == "low")
        metric("High Priority Decisions",   high_priority)
        metric("Medium Priority Decisions", medium_priority)
        metric("Low Priority Decisions",    low_priority)

        avg_conf = sum(d.confidence for d in context.decisions) / len(context.decisions)
        avg_unc  = sum(d.uncertainty for d in context.decisions) / len(context.decisions)
        metric("Decision Confidence", f"{avg_conf:.3f}")
        metric("Decision Uncertainty", f"{avg_unc:.3f}")

        # Organisation Intelligence summary
        org = context.org_intelligence
        if org:
            section("Organization Intelligence Summary")
            metric("Org Health (average)", f"{org.health.average_health:.3f}")
            metric("Healthy Topics",       org.health.healthy_count)
            metric("Warning Topics",       org.health.warning_count)
            metric("Critical Topics",      org.health.critical_count)

            high_kr = sum(1 for r in org.knowledge_risks if r.risk_level == "HIGH")
            metric("High Knowledge Risks", high_kr)

            bf1 = sum(1 for b in org.bus_factors if b.bus_factor == 1)
            metric("Bus Factor = 1 Topics", bf1)

            metric("Forecast", "UNAVAILABLE (single snapshot)")

            exec_recs = [r for r in org.recommendations if r.action_type == "executive"]
            if exec_recs:
                ranking(
                    "Executive Recommendations",
                    [f"[{r.priority.upper():<6}] {r.action[:90]}" for r in exec_recs[:5]],
                )
        else:
            metric("Organization Intelligence", "Not available")

        ranking(
            "Executive Actions (from Decisions)",
            [
                f"{item.priority:<8} {item.action}"
                for item in context.decisions[:10]
            ],
        )
        lineage("Canonical Lineage")
        success("Executive dashboard rendered from canonical outputs")
