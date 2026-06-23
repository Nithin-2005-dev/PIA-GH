from app.simulation.developer_departure_policy import (
    DeveloperDeparturePolicy,
)


class SimulationService:

    def __init__(self):

        self._policy = (
            DeveloperDeparturePolicy()
        )

    def simulate_departure(
        self,
        health_report,
        ownership_estimate,
        readiness_score: float,
    ):

        return (
            self._policy.simulate(
                module_ref=(
                    ownership_estimate.module_ref
                ),
                health_score=(
                    health_report.health_score
                ),
                ownership_share=(
                    ownership_estimate.ownership_percentage
                ),
                readiness_score=(
                    readiness_score
                ),
                developer_name=(
                    ownership_estimate.owner_ref.id
                ),
            )
        )