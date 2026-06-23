from app.simulation.simulation_service import (
    SimulationService,
)


class SimulationEngine:

    def __init__(self):

        self._service = (
            SimulationService()
        )

    def simulate(
        self,
        scenario,
        health_report,
        ownership_estimate,
        readiness_score: float,
    ):

        return (
            self._service.simulate_departure(
                health_report=(
                    health_report
                ),
                ownership_estimate=(
                    ownership_estimate
                ),
                readiness_score=(
                    readiness_score
                ),
            )
        )