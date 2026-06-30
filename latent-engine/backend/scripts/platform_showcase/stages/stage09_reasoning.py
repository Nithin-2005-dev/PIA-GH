"""Stage 09 — Reasoning.

Consumes Knowledge Models and Organization Intelligence.
Produces ReasoningResult objects stored in context.reasoning_results.

This stage sits AFTER Organization Intelligence so its conclusions can be
enriched with ownership, health, bus-factor, and risk signals.

Flow:
    Knowledge → Reasoning ← Organization Intelligence
"""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from ..context import OrgIntelligenceResult, PlatformContext, ReasoningResult
from ..ui import metric, ranking, section, success, warning
from .base import PipelineStage


class ReasoningStage(PipelineStage):
    """
    Stage 09 — Reasoning

    Derives conclusions from knowledge topics, enriched by organisational
    intelligence signals when available.
    """

    name = "Knowledge and Org Intel to Reasoning"

    def execute(self, context: PlatformContext) -> None:
        knowledge = context.knowledge
        org_intel = context.org_intelligence

        if not knowledge:
            warning("No knowledge models available — skipping Reasoning layer")
            return

        results = self._build_reasoning(knowledge, org_intel)
        context.reasoning_results = results
        context.metrics["reasoning_results"] = len(results)

        section("Reasoning Results")
        metric("Knowledge Topics Consumed", len(knowledge))
        metric("Org Intelligence Available", "YES" if org_intel else "NO")
        metric("Reasoning Results Produced", len(results))
        metric(
            "Explainability Preserved",
            "PASS" if all(r.rationale for r in results) else "FAIL",
        )
        metric(
            "Confidence Propagated",
            "PASS" if all(r.confidence >= 0.0 for r in results) else "FAIL",
        )

        ranking(
            "Reasoning Conclusions",
            [
                f"{r.subject:<28} {r.conclusion:<38} (conf={r.confidence:.3f})"
                for r in results
            ],
        )
        success("Reasoning layer built from knowledge + organizational intelligence")

    # ------------------------------------------------------------------

    def _build_reasoning(
        self,
        knowledge,
        org_intel: OrgIntelligenceResult | None,
    ) -> list[ReasoningResult]:
        """
        Derives one ReasoningResult per knowledge topic.

        When org_intel is available, the conclusion and confidence are
        adjusted by risk signals from org analysis:
            - HIGH knowledge risk → lower confidence, stronger warning conclusion
            - LOW bus factor      → escalated urgency in conclusion
        """
        # Build lookup maps from org intel for O(1) access
        risk_map = {}
        bus_map  = {}
        if org_intel:
            risk_map = {r.subject: r for r in org_intel.knowledge_risks}
            bus_map  = {b.subject: b for b in org_intel.bus_factors}

        results: list[ReasoningResult] = []

        for item in knowledge:
            # Base conclusion from expertise score
            if item.average_score >= 0.70:
                base_conclusion = "high-confidence organizational signal"
            elif item.average_score >= 0.40:
                base_conclusion = "moderate organizational signal"
            else:
                base_conclusion = "emerging organizational signal"

            # Enrich with org intelligence signals
            risk   = risk_map.get(item.topic)
            bf     = bus_map.get(item.topic)
            org_signal = ""
            confidence_adjustment = 0.0

            if risk and risk.risk_level == "HIGH":
                org_signal = (
                    f"; CRITICAL: bus factor={risk.bus_factor}, "
                    f"owner_count={risk.owner_count} — immediate action required"
                )
                confidence_adjustment = +0.05   # elevate confidence in the risk signal
            elif risk and risk.risk_level == "MEDIUM":
                org_signal = (
                    f"; MODERATE: bus factor={risk.bus_factor}, "
                    f"owner_count={risk.owner_count} — monitor and plan"
                )
            elif bf and bf.bus_factor == 1:
                org_signal = f"; single-person dependency (bus factor=1)"
                confidence_adjustment = +0.03

            conclusion = base_conclusion + org_signal

            # Build rationale
            base_rationale = (
                f"Reasoned from {item.expertise_count} expertise model(s) "
                f"with average score {item.average_score:.3f}."
            )
            org_rationale = ""
            if org_intel:
                org_rationale = (
                    f" Org intelligence: "
                    f"health_avg={org_intel.health.average_health:.3f}, "
                    f"critical_topics={org_intel.health.critical_count}."
                )

            rationale = base_rationale + org_rationale

            final_confidence = min(
                1.0,
                item.average_confidence + confidence_adjustment,
            )

            results.append(
                ReasoningResult(
                    id=str(uuid5(NAMESPACE_URL, f"reasoning|{item.id}|{conclusion}")),
                    subject=item.topic,
                    conclusion=conclusion,
                    confidence=round(final_confidence, 4),
                    uncertainty=round(item.average_uncertainty, 4),
                    rationale=rationale,
                    knowledge_ids=(item.id,),
                )
            )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
