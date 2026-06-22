from abc import ABC, abstractmethod

from app.query.query_result import QueryResult

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)


class OwnershipPolicy(ABC):

    @abstractmethod
    def calculate(
        self,
        experts: list[QueryResult],
    ) -> list[OwnershipEstimate]:
        pass