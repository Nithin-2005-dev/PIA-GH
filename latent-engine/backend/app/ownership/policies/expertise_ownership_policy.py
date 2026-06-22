from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.query.query_result import QueryResult

from .ownership_policy import (
    OwnershipPolicy,
)


class ExpertiseOwnershipPolicy(
    OwnershipPolicy
):

    def calculate(
        self,
        experts: list[QueryResult],
    ) -> list[OwnershipEstimate]:

        if not experts:
            return []

        total_score = sum(
            expert.effective_score
            for expert in experts
        )

        if total_score == 0:
            return []

        ownership = []

        for expert in experts:

            ownership_percentage = (
                expert.effective_score
                / total_score
            )

            if ownership_percentage >= 0.60:

                level = (
                    OwnershipLevel.PRIMARY
                )

            elif ownership_percentage >= 0.20:

                level = (
                    OwnershipLevel.SECONDARY
                )

            else:

                level = (
                    OwnershipLevel.CONTRIBUTOR
                )

            ownership.append(
                OwnershipEstimate(
                    owner_ref=(
                        expert.estimate
                        .developer_ref
                    ),
                    module_ref=(
                        expert.estimate
                        .module_ref
                    ),
                    ownership_percentage=(
                        ownership_percentage
                    ),
                    effective_score=(
                        expert.effective_score
                    ),
                    ownership_level=level,
                )
            )

        ownership.sort(
            key=lambda estimate: (
                estimate.ownership_percentage
            ),
            reverse=True,
        )

        return ownership