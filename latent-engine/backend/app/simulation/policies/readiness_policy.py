from abc import ABC
from abc import abstractmethod

from app.query.query_result import (
    QueryResult,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
)


class ReadinessPolicy(
    ABC
):

    @abstractmethod
    def compute(
        self,
        successor: SuccessorCandidate | None,
        expertise: QueryResult,
    ) -> float:
        pass