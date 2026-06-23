from .simulation_result import (
    SimulationResult,
)


class DeveloperDeparturePolicy:

    def simulate(
        self,
        module_ref,
        health_score: float,
        ownership_share: float,
        readiness_score: float,
        developer_name: str,
    ):

        knowledge_loss = (

            ownership_share

            *

            (
                1
                -
                readiness_score
            )
        )

        health_after = (

            health_score

            *

            (
                1
                -
                knowledge_loss
            )
        )

        impact = (
            health_after
            -
            health_score
        )

        if health_after >= 75:

            severity = "LOW"

        elif health_after >= 50:

            severity = "MODERATE"

        elif health_after >= 25:

            severity = "HIGH"

        else:

            severity = "CRITICAL"

        return SimulationResult(
            module_ref=module_ref,
            scenario=(
                f"{developer_name} leaves"
            ),
            health_before=(
                health_score
            ),
            health_after=(
                health_after
            ),
            impact=impact,
            knowledge_loss=(
                knowledge_loss
            ),
            severity=severity,
        )