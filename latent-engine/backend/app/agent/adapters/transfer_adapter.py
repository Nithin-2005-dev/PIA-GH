from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.knowledge_transfer.policies.simple_transfer_policy import (
    SimpleTransferPolicy,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.successor.successor_candidate import (
    SuccessorCandidate,
)


class TransferAdapter:

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
            "payments.py"
        )

        if (
            self._intelligence
            is not None
        ):

            ownerships = (
                self._intelligence
                .ownership_service
                .owners_of(
                    module_id
                )
            )

            successors = (
                self._intelligence
                .successor_service
                .recommend(
                    module_id,
                    limit=3,
                )
            )

            concentration_reports = (
                self._intelligence
                .concentration_service
                .analyze(
                    self._intelligence
                    .projection
                    .all_estimates()
                )
            )

            plans = (
                self._intelligence
                .transfer_service
                .plans(
                    ownerships,
                    successors,
                    concentration_reports,
                )
            )

        else:

            module_ref = EntityRef(
                id=module_id,
                type=EntityType.FILE,
            )

            ownerships = [

                OwnershipEstimate(
                    owner_ref=EntityRef(
                        id="david",
                        type=EntityType.DEVELOPER,
                    ),
                    module_ref=module_ref,
                    ownership_percentage=0.90,
                    effective_score=95,
                    ownership_level=(
                        OwnershipLevel.PRIMARY
                    ),
                )
            ]

            successors = [

                SuccessorCandidate(
                    developer_ref=EntityRef(
                        id="emma",
                        type=EntityType.DEVELOPER,
                    ),
                    module_ref=module_ref,
                    score=70,
                    rank=1,
                )
            ]

            concentration_reports = [

                ConcentrationReport(
                    module_ref=module_ref,
                    expert_count=3,
                    concentration_score=0.98,
                    concentration_level="HIGH",
                )
            ]

            plans = (
                SimpleTransferPolicy()
                .recommend(
                    ownerships,
                    successors,
                    concentration_reports,
                )
            )

        if not plans:
            return (
                "No transfer opportunities found."
            )

        plan = plans[0]

        return (
            f"Module: "
            f"{plan.module_ref.id}\n"
            f"Mentor: "
            f"{plan.mentor_ref.id}\n"
            f"Learner: "
            f"{plan.learner_ref.id}\n"
            f"Priority: "
            f"{plan.priority_score:.2f}\n"
            f"Reason: "
            f"{plan.reason}"
        )
