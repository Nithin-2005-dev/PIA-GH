from abc import ABC, abstractmethod

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
)


class SuccessorPolicy(ABC):

    @abstractmethod
    def recommend(
        self,
        ownership: list[OwnershipEstimate],
        limit: int,
    ) -> list[SuccessorCandidate]:
        pass