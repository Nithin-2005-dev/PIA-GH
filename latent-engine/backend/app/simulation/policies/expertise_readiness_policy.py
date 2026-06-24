from app.query.query_result import (
    QueryResult,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
)

from .readiness_policy import (
    ReadinessPolicy,
)


class ExpertiseReadinessPolicy(
    ReadinessPolicy
):

    def compute(
        self,
        successor: SuccessorCandidate | None,
        expertise: QueryResult,
    ) -> float:

        normalized_expertise = min(
            expertise.estimate.raw_score
            / 100.0,
            1.0,
        )

        confidence = (
            expertise.estimate.confidence
        )

        rank_bonus = 0.0

        if successor is not None:

            if successor.rank == 1:
                rank_bonus = 0.2

            elif successor.rank == 2:
                rank_bonus = 0.1

        readiness = (

            normalized_expertise
            * confidence

            +

            rank_bonus
        )

        return min(
            readiness,
            1.0,
        )