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

        module = EntityRef(
            id=module_id,
            type=EntityType.FILE,
        )

        # M27.1 — Ground Ownership: replace hardcoded fixture with real ownership data
        owners = None
        if self._intelligence is not None:
            owners = (
                self._intelligence
                .ownership_service
                .owners_of(
                    module_id
                )
            )

        if not owners:
            return "No ownership data found."

        ownership = owners[0]

        # M27.3 — Ground Departure Target: use primary owner as default departure candidate
        developer_id = (
            context.developer_id
            or
            ownership.owner_ref.id
        )

        owner = EntityRef(
            id=developer_id,
            type=EntityType.DEVELOPER,
        )

        # Find the ownership estimate for the specific developer
        developer_ownership = next(
            (
                o for o in owners
                if o.owner_ref.id == developer_id
            ),
            None,
        )

        if developer_ownership is None:
            return (
                f"No ownership data found for "
                f"developer '{developer_id}'."
            )

        ownership = developer_ownership

        health_report = HealthReport(
            module_ref=module,
            health_score=80,
            health_level="HEALTHY",
            coverage_score=80,
            concentration_score=0.30,
            bus_factor=4,
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

            # M27.2 — Ground Health: replace hardcoded fixture with real health pipeline
            estimates = (
                self._intelligence
                .projection
                .all_estimates()
            )

            coverage_reports = (
                self._intelligence
                .coverage_service
                .analyze(
                    estimates
                )
            )

            concentration_reports = (
                self._intelligence
                .concentration_service
                .analyze(
                    estimates
                )
            )

            bus_factor = (
                self._intelligence
                .bus_factor_service
                .analyze(
                    module_id
                )
            )

            health_reports = (
                self._intelligence
                .health_service
                .analyze(
                    coverage_reports,
                    concentration_reports,
                    [bus_factor],
                )
            )

            health_report = next(
                (
                    report
                    for report in health_reports
                    if report.module_ref.id
                    == module_id
                ),
                None,
            )

            if health_report is None:
                return "No health data found."

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