from dataclasses import dataclass

from app.evidence.domain import Evidence


@dataclass(frozen=True)
class EvidenceRankingPolicy:
    confidence_weight: float = 0.25
    severity_weight: float = 0.2
    business_impact_weight: float = 0.15
    architectural_impact_weight: float = 0.1
    security_impact_weight: float = 0.1
    operational_impact_weight: float = 0.1
    urgency_weight: float = 0.05
    novelty_weight: float = 0.025
    persistence_weight: float = 0.025


class EvidenceRankingEngine:

    def __init__(
        self,
        policy: EvidenceRankingPolicy | None = None,
    ):
        self._policy = policy or EvidenceRankingPolicy()

    def score(
        self,
        evidence: Evidence,
    ) -> float:
        metadata = evidence.metadata

        business_impact = float(
            metadata.get(
                "business_impact",
                evidence.severity.rank() / 4.0,
            )
        )
        architectural_impact = float(
            metadata.get(
                "architectural_impact",
                1.0 if evidence.category == "architecture" else 0.5,
            )
        )
        security_impact = float(
            metadata.get(
                "security_impact",
                1.0 if evidence.category == "security" else 0.0,
            )
        )
        operational_impact = float(
            metadata.get(
                "operational_impact",
                1.0
                if evidence.category == "operational_risk"
                else 0.5,
            )
        )

        return (
            evidence.confidence * self._policy.confidence_weight
            + (evidence.severity.rank() / 4.0)
            * self._policy.severity_weight
            + business_impact
            * self._policy.business_impact_weight
            + architectural_impact
            * self._policy.architectural_impact_weight
            + security_impact
            * self._policy.security_impact_weight
            + operational_impact
            * self._policy.operational_impact_weight
            + (evidence.priority.rank() / 3.0)
            * self._policy.urgency_weight
            + evidence.historical_context.novelty
            * self._policy.novelty_weight
            + evidence.historical_context.persistence
            * self._policy.persistence_weight
        )

    def rank(
        self,
        evidence: tuple[Evidence, ...],
    ) -> tuple[Evidence, ...]:
        return tuple(
            sorted(
                evidence,
                key=self.score,
                reverse=True,
            )
        )

