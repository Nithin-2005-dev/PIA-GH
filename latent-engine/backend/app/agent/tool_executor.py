from app.agent.agent_response import (
    AgentResponse,
)

from app.agent.tool_route import (
    ToolRoute,
)

from app.agent.adapters.risk_adapter import (
    RiskAdapter,
)

from app.agent.adapters.forecast_adapter import (
    ForecastAdapter,
)

from app.agent.adapters.intervention_adapter import (
    InterventionAdapter,
)

from app.agent.adapters.simulation_adapter import (
    SimulationAdapter,
)


class ToolExecutor:

    def __init__(self):

        self._risk = (
            RiskAdapter()
        )

        self._forecast = (
            ForecastAdapter()
        )

        self._intervention = (
            InterventionAdapter()
        )

        self._simulation = (
            SimulationAdapter()
        )

    def execute(
        self,
        intent,
        route,
    ):

        if route == ToolRoute.RISK:

            summary = (
                self._risk.execute()
            )

        elif route == ToolRoute.FORECAST:

            summary = (
                self._forecast.execute()
            )

        elif route == ToolRoute.INTERVENTION:

            summary = (
                self._intervention.execute()
            )

        else:

            summary = (
                self._simulation.execute()
            )

        return AgentResponse(
            intent=intent.value,
            route=route.value,
            summary=summary,
        )