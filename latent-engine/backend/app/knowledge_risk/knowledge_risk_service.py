from app.ownership.ownership_service import (
    OwnershipService,
)

from app.risk.bus_factor_service import (
    BusFactorService,
)

from .knowledge_risk import (
    KnowledgeRisk,
)

from .policies.knowledge_risk_policy import (
    KnowledgeRiskPolicy,
)


class KnowledgeRiskService:

    def __init__(
        self,
        ownership_service: OwnershipService,
        bus_factor_service: BusFactorService,
        policy: KnowledgeRiskPolicy,
    ):
        self._ownership_service = (
            ownership_service
        )

        self._bus_factor_service = (
            bus_factor_service
        )

        self._policy = policy

    def analyze(
        self,
        module_id: str,
    ) -> KnowledgeRisk:

        ownership = (
            self._ownership_service
            .owners_of(module_id)
        )

        bus_factor = (
            self._bus_factor_service
            .analyze(module_id)
        )

        return (
            self._policy.evaluate(
                bus_factor,
                len(ownership),
            )
        )