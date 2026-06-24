from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.health.health_report import (
    HealthReport,
)

from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.ownership.ownership_level import (
    OwnershipLevel,
)

from app.simulation.simulation_service import (
    SimulationService,
)


class SimulationAdapter:

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

        developer_id = (
            context.developer_id
            or
            "alice"
        )

        module = EntityRef(
            id=module_id,
            type=EntityType.FILE,
        )

        owner = EntityRef(
            id=developer_id,
            type=EntityType.DEVELOPER,
        )

        health_report = HealthReport(
            module_ref=module,
            health_score=80,
            health_level="HEALTHY",
            coverage_score=80,
            concentration_score=0.30,
            bus_factor=4,
        )

        ownership = OwnershipEstimate(
            owner_ref=owner,
            module_ref=module,
            ownership_percentage=0.75,
            effective_score=120,
            ownership_level=(
                OwnershipLevel.PRIMARY
            ),
        )

        readiness_score = 0.60
        successor_name = "unknown"

        if (
            self._intelligence
            is not None
        ):

            successors = (
                self._intelligence
                .successor_service
                .recommend(
                    module_id,
                    limit=1,
                )
            )

            if successors:

                successor_name = (
                    successors[0]
                    .developer_ref
                    .id
                )

                readiness = (
                    self._intelligence
                    .readiness_service
                    .readiness_of(
                        successor_name,
                        module_id,
                    )
                )

                readiness_score = (
                    readiness
                    .readiness_score
                )

        result = (
            SimulationService()
            .simulate_departure(
                health_report=health_report,
                ownership_estimate=ownership,
                readiness_score=(
                    readiness_score
                ),
            )
        )

        return (
            f"Successor: "
            f"{successor_name}\n"
            f"Health Before: "
            f"{result.health_before:.2f}\n"
            f"Health After: "
            f"{result.health_after:.2f}\n"
            f"Knowledge Loss: "
            f"{result.knowledge_loss:.2f}\n"
            f"Impact: "
            f"{result.impact:.2f}\n"
            f"Severity: "
            f"{result.severity}"
        )