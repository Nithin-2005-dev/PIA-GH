from abc import ABC, abstractmethod

from app.risk.bus_factor import (
    BusFactor,
)

from app.knowledge_risk.knowledge_risk import (
    KnowledgeRisk,
)


class KnowledgeRiskPolicy(ABC):

    @abstractmethod
    def evaluate(
        self,
        bus_factor: BusFactor,
        owner_count: int,
    ) -> KnowledgeRisk:
        pass