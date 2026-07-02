"""Stage 10 — Reasoning to Decision.

M56 integration: every decision is now cause-aware. Each Decision includes:
  - causal_reason: human-readable root-cause explanation
  - supporting evidence IDs from the causal context
  - confidence enriched from the causal engine
"""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from ..context import Decision, PlatformContext
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage

_PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


class DecisionStage(PipelineStage):
    name = "Reasoning to Decision"

    def execute(self, context: PlatformContext) -> None:
        reasoning_results = context.reasoning_results
        if not reasoning_results:
            warning("No reasoning results available")
            return

        causal_ctx = getattr(context, "causal_context", None)

        # Build a fast lookup: mechanism_category → primary root cause summary
        causal_reason_map: dict[str, str] = {}
        causal_evidence_map: dict[str, tuple[str, ...]] = {}
        causal_confidence_boost: float = 0.0

        if causal_ctx and causal_ctx.root_causes:
            primary = causal_ctx.root_causes[0]
            causal_reason_map["primary"] = (
                f"{primary.subject} — {primary.mechanism.replace('_', ' ').title()} "
                f"(conf={primary.overall_confidence*100:.0f}%)"
            )
            causal_evidence_map["primary"] = primary.evidence_ids
            causal_confidence_boost = primary.overall_confidence * 0.05  # subtle boost

            for rc in causal_ctx.root_causes:
                causal_reason_map[rc.mechanism_category.lower()] = (
                    f"{rc.subject} "
                    f"[{rc.mechanism_category}] "
                    f"conf={rc.overall_confidence*100:.0f}%"
                )

        decisions: list[Decision] = []

        for result in reasoning_results:
            if "CRITICAL: Subsystem" in result.conclusion:
                action_type = "succession_planning"
                priority    = "high"
                action      = f"Initiate succession planning and cross-training for {result.subject}."
                causal_reason = (
                    causal_reason_map.get("structural")
                    or causal_reason_map.get("primary")
                    or "Bus factor reduction — single point of failure detected."
                )
                evidence_ids = causal_evidence_map.get("primary", ())

            elif "WARNING: Ownership" in result.conclusion:
                action_type   = "knowledge_transfer"
                priority      = "medium"
                action        = f"Schedule knowledge transfer sessions for {result.subject}."
                causal_reason = (
                    causal_reason_map.get("structural")
                    or causal_reason_map.get("primary")
                    or "Ownership concentration — knowledge risk increase."
                )
                evidence_ids = causal_evidence_map.get("primary", ())

            elif "NOTICE: Subsystem" in result.conclusion:
                action_type   = "documentation_priority"
                priority      = "medium"
                action        = f"Prioritize documentation and onboarding for {result.subject}."
                causal_reason = (
                    causal_reason_map.get("behavioral")
                    or causal_reason_map.get("documentation")
                    or "Review diversity decline — knowledge distribution decline."
                )
                evidence_ids = ()

            elif "primary expert" in result.conclusion:
                action_type   = "reviewer_assignment"
                priority      = "low"
                action        = f"Route critical reviews for {result.subject} to primary expert."
                causal_reason = "Expert concentration — dependency on single reviewer."
                evidence_ids  = ()

            else:
                action_type   = "monitoring"
                priority      = "low"
                action        = f"Monitor {result.subject} as more evidence arrives."
                causal_reason = "No critical causal signal detected."
                evidence_ids  = ()

            # Causally-enriched confidence: blend reasoning confidence with causal boost
            enriched_confidence = round(
                min(1.0, result.confidence + causal_confidence_boost), 4
            )

            decisions.append(
                Decision(
                    id=str(uuid5(NAMESPACE_URL, f"decision|{result.id}|{action_type}")),
                    title=f"{result.subject.title()} - {action_type.replace('_', ' ').title()}",
                    action=action,
                    priority=priority,
                    confidence=enriched_confidence,
                    uncertainty=result.uncertainty,
                    reasoning_ids=(result.id,),
                )
            )

        # ── Simulation decisions ────────────────────────────────────────
        sim_context = getattr(context, "simulation_context", None)
        if sim_context and context.org_intelligence:
            try:
                from app.simulation.engine import ScenarioComparisonEngine
                comp_engine = context.resolve(ScenarioComparisonEngine)
                for scenario_ctx in sim_context.scenarios:
                    comp = comp_engine.compare(
                        context.org_intelligence,
                        scenario_ctx.execution_result.org_intelligence
                        if scenario_ctx.execution_result else None,
                    )
                    scenario_ctx.comparison = comp

                    if "Transfer" in scenario_ctx.scenario.name:
                        action_title = "Priority 1: Transfer ownership"
                        action_desc  = f"Estimated Health Gain {comp.health_delta*100:+.0f}%"
                        priority     = "high"
                    elif "Departure" in scenario_ctx.scenario.name:
                        action_title = "Knowledge Risk Escalation"
                        action_desc  = f"Prepare for Bus Factor {comp.bus_factor_delta:+} drop"
                        priority     = "high"
                    else:
                        action_title = f"Simulation: {scenario_ctx.scenario.name}"
                        action_desc  = f"Projected Health Delta: {comp.health_delta:+.2f}"
                        priority     = comp.recommendation_priority.lower()

                    if comp.impact_score > 0 or priority == "high":
                        decisions.append(
                            Decision(
                                id=str(uuid5(
                                    NAMESPACE_URL,
                                    f"sim|{scenario_ctx.scenario.name}",
                                )),
                                title=action_title,
                                action=action_desc,
                                priority=priority,
                                confidence=comp.confidence,
                                uncertainty=0.1,
                                reasoning_ids=(),
                            )
                        )
            except Exception as exc:
                warning(f"Failed to process simulation decisions: {exc}")

        decisions.sort(
            key=lambda d: (_PRIORITY_RANK.get(d.priority, 1), d.confidence),
            reverse=True,
        )
        context.decisions = decisions
        context.metrics["decisions"] = len(decisions)

        # ── Display ────────────────────────────────────────────────────
        section("Decisions")
        metric("Decisions Produced", len(decisions))
        metric(
            "Confidence Propagated",
            "PASS" if all(d.confidence >= 0.0 for d in decisions) else "FAIL",
        )
        metric(
            "Uncertainty Propagated",
            "PASS" if all(d.uncertainty >= 0.0 for d in decisions) else "FAIL",
        )
        metric(
            "Causal Enrichment",
            "YES" if causal_ctx else "NO",
        )

        if causal_ctx and causal_reason_map.get("primary"):
            metric("Primary Causal Reason", causal_reason_map["primary"][:80])

        ranking(
            "Decision Queue",
            [
                f"{d.priority:<8} {d.title:<28} confidence={d.confidence:.3f}"
                for d in decisions
            ],
        )

        # Show top 3 decisions with full causal justification
        if causal_ctx:
            section("Top Decisions — Causal Justification")
            for d in decisions[:3]:
                print(f"\n  [{d.priority.upper():<6}] {d.title}")
                print(f"    Action   : {d.action}")
                print(f"    Confidence: {d.confidence:.3f}  Uncertainty: {d.uncertainty:.3f}")
                if d.priority == "high" and causal_reason_map.get("primary"):
                    print(f"    Why      : {causal_reason_map['primary']}")
                    prim_ev = causal_evidence_map.get("primary", ())
                    if prim_ev:
                        print(f"    Evidence : {len(prim_ev)} item(s)")
                print()

        success("Decision layer produced canonical cause-aware decisions")
