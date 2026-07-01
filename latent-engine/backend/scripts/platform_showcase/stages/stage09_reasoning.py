"""Stage 09 — Reasoning.

Consumes Knowledge Models and Organization Intelligence.
Produces ReasoningResult objects stored in context.reasoning_results.

This stage sits AFTER Organization Intelligence so its conclusions can be
enriched with ownership, health, bus-factor, and risk signals.

Flow:
    Knowledge → Reasoning ← Organization Intelligence
"""

from __future__ import annotations

from collections import defaultdict
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
        risk_map = {}
        bus_map  = {}
        coverage_map = {}
        concentration_map = {}
        ownership_by_dev = defaultdict(list)
        
        if org_intel:
            risk_map = {r.subject: r for r in org_intel.knowledge_risks}
            bus_map  = {b.subject: b for b in org_intel.bus_factors}
            coverage_map = {c.subject: c for c in org_intel.coverage}
            concentration_map = {c.subject: c for c in org_intel.concentration}
            for o in org_intel.ownership:
                ownership_by_dev[o.subject].append(o)

        results: list[ReasoningResult] = []

        for item in knowledge:
            conclusion = ""
            confidence_adjustment = 0.0
            rationale_parts = []
            
            if item.entity_type == "developer":
                primary = [o.category for o in ownership_by_dev.get(item.topic, []) if o.ownership_level == "PRIMARY"]
                if primary:
                    conclusion = f"Developer {item.topic} is the primary expert for {', '.join(primary)}."
                    confidence_adjustment += 0.1
                else:
                    conclusion = f"Developer {item.topic} provides broad support across multiple subsystems."
            
            elif item.entity_type == "subsystem":
                bf = bus_map.get(item.topic)
                risk = risk_map.get(item.topic)
                cov = coverage_map.get(item.topic)
                conc = concentration_map.get(item.topic)
                
                if bf and bf.bus_factor <= 1:
                    conclusion = f"CRITICAL: Subsystem {item.topic} has a bus factor of {bf.bus_factor} with {bf.coverage:.0f}% coverage gap."
                    confidence_adjustment += 0.2
                    rationale_parts.append(f"Single point of failure detected in {item.topic}.")
                elif conc and conc.risk_level == "HIGH":
                    conclusion = f"WARNING: Ownership in {item.topic} is highly concentrated (risk score={conc.concentration_score:.2f})."
                    confidence_adjustment += 0.1
                elif cov and cov.coverage_level == "WEAK":
                    conclusion = f"NOTICE: Subsystem {item.topic} has weak knowledge coverage ({cov.expert_count} experts)."
                else:
                    conclusion = f"Subsystem {item.topic} is stable and adequately covered."
            
            else:
                conclusion = f"Topic {item.topic} requires ongoing monitoring."

            base_rationale = (
                f"Derived from {item.expertise_count} expertise model(s) "
                f"with score {item.average_score:.3f}. "
            )
            rationale = base_rationale + " ".join(rationale_parts)

            final_confidence = min(1.0, item.average_confidence + confidence_adjustment)

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
