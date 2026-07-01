"""Stage 10 — Reasoning to Decision."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from ..context import Decision, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class DecisionStage(PipelineStage):
    name = "Reasoning to Decision"

    def execute(self, context: PlatformContext) -> None:
        reasoning_results = context.reasoning_results
        if not reasoning_results:
            warning("No reasoning results available")
            return

        decisions = []
        for result in reasoning_results:
            if "CRITICAL: Subsystem" in result.conclusion:
                action_type = "succession_planning"
                priority = "high"
                action = f"Initiate succession planning and cross-training for {result.subject}."
            elif "WARNING: Ownership" in result.conclusion:
                action_type = "knowledge_transfer"
                priority = "medium"
                action = f"Schedule knowledge transfer sessions for {result.subject}."
            elif "NOTICE: Subsystem" in result.conclusion:
                action_type = "documentation_priority"
                priority = "medium"
                action = f"Prioritize documentation and onboarding for {result.subject}."
            elif "primary expert" in result.conclusion:
                action_type = "reviewer_assignment"
                priority = "low"
                action = f"Route critical reviews for {result.subject} to primary expert."
            else:
                action_type = "monitoring"
                priority = "low"
                action = f"Monitor {result.subject} as more evidence arrives."

            decisions.append(
                Decision(
                    id=str(uuid5(NAMESPACE_URL, f"decision|{result.id}|{action_type}")),
                    title=f"{result.subject.title()} - {action_type.replace('_', ' ').title()}",
                    action=action,
                    priority=priority,
                    confidence=result.confidence,
                    uncertainty=result.uncertainty,
                    reasoning_ids=(result.id,),
                )
            )

        priority_rank = {"high": 3, "medium": 2, "low": 1}
        decisions.sort(
            key=lambda item: (priority_rank[item.priority], item.confidence),
            reverse=True,
        )
        context.decisions = decisions
        context.metrics["decisions"] = len(decisions)

        section("Decisions")
        metric("Decisions Produced", len(decisions))
        metric(
            "Confidence Propagated",
            "PASS" if all(item.confidence >= 0.0 for item in decisions) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(item.uncertainty >= 0.0 for item in decisions) else "FAIL",
        )
        ranking(
            "Decision Queue",
            [
                (
                    f"{item.priority:<8} {item.title:<28} "
                    f"confidence={item.confidence:.3f}"
                )
                for item in decisions
            ],
        )
        success("Decision layer produced canonical decisions")
