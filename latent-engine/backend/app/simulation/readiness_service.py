from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from app.simulation.successor_readiness import (
    SuccessorReadiness,
)

from app.successor.successor_service import (
    SuccessorService,
)

from .policies.readiness_policy import (
    ReadinessPolicy,
)


class ReadinessService:

    def __init__(
        self,
        successor_service: SuccessorService,
        query_service: ExpertiseQueryService,
        policy: ReadinessPolicy,
    ):

        self._successor_service = (
            successor_service
        )

        self._query_service = (
            query_service
        )

        self._policy = policy

    def readiness_of(
        self,
        developer_id: str,
        module_id: str,
    ) -> SuccessorReadiness:

        experts = (
            self._query_service
            .module_experts(
                module_id
            )
        )

        expertise = next(
            (
                expert
                for expert in experts
                if (
                    expert
                    .estimate
                    .developer_ref
                    .id
                    ==
                    developer_id
                )
            ),
            None,
        )

        if expertise is None:

            return SuccessorReadiness(
                successor=developer_id,
                readiness_score=0.0,
            )

        successors = (
            self._successor_service
            .recommend(
                module_id,
                limit=10,
            )
        )

        successor = next(
            (
                candidate
                for candidate
                in successors
                if (
                    candidate
                    .developer_ref
                    .id
                    ==
                    developer_id
                )
            ),
            None,
        )

        score = (
            self._policy.compute(
                successor,
                expertise,
            )
        )

        return SuccessorReadiness(
            successor=developer_id,
            readiness_score=score,
        )

    def rank(
        self,
        module_id: str,
        limit: int = 10,
    ):

        successors = (
            self._successor_service
            .recommend(
                module_id,
                limit=limit,
            )
        )

        readiness = []

        for successor in successors:

            readiness.append(
                self.readiness_of(
                    successor.developer_ref.id,
                    module_id,
                )
            )

        readiness.sort(
            key=lambda item: (
                item.readiness_score
            ),
            reverse=True,
        )

        return readiness