from abc import ABC, abstractmethod

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.risk.bus_factor import (
    BusFactor,
)


class BusFactorPolicy(ABC):

    @abstractmethod
    def calculate(
        self,
        ownership: list[OwnershipEstimate],
    ) -> BusFactor:
        pass