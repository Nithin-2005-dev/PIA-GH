from dataclasses import dataclass

from app.domain.entity_ref import (
    EntityRef,
)


@dataclass(frozen=True)
class SimulationScenario:
    """
    Simulation request.
    """

    module_ref: EntityRef

    departing_owner: str