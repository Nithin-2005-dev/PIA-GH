from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class SimulationResult:

    module_ref: EntityRef

    scenario: str

    health_before: float

    health_after: float

    impact: float

    knowledge_loss: float

    severity: str