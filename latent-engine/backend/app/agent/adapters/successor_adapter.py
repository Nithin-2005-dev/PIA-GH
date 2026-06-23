from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.successor.policies.expertise_successor_policy import (
    ExpertiseSuccessorPolicy,
)


class SuccessorAdapter:

    def __init__(
        self,
        intelligence_context=None,
    ):
        self._intelligence = (
            intelligence_context
        )

    def execute(
        self,
        context,
    ):

        module_id = (
            context.module_id
            or
            "auth.py"
        )

        module_ref = EntityRef(
            id=module_id,
            type=EntityType.FILE,
        )

        ownership = [

            OwnershipEstimate(
                owner_ref=EntityRef(
                    id="alice",
                    type=EntityType.DEVELOPER,
                ),
                module_ref=module_ref,
                ownership_percentage=0.70,
                effective_score=70,
                ownership_level=(
                    OwnershipLevel.PRIMARY
                ),
            ),

            OwnershipEstimate(
                owner_ref=EntityRef(
                    id="bob",
                    type=EntityType.DEVELOPER,
                ),
                module_ref=module_ref,
                ownership_percentage=0.20,
                effective_score=20,
                ownership_level=(
                    OwnershipLevel.SECONDARY
                ),
            ),

            OwnershipEstimate(
                owner_ref=EntityRef(
                    id="charlie",
                    type=EntityType.DEVELOPER,
                ),
                module_ref=module_ref,
                ownership_percentage=0.10,
                effective_score=10,
                ownership_level=(
                    OwnershipLevel.CONTRIBUTOR
                ),
            ),
        ]

        if (
            self._intelligence
            is not None
        ):

            candidates = (
                self._intelligence
                .successor_service
                .recommend(
                    module_id,
                    limit=3,
                )
            )

        else:

            candidates = (
                ExpertiseSuccessorPolicy()
                .recommend(
                    ownership,
                    limit=3,
                )
            )

        lines = []

        for candidate in candidates:

            lines.append(
                f"#{candidate.rank} "
                f"{candidate.developer_ref.id} "
                f"({candidate.score:.2f})"
            )

        return "\n".join(lines)
