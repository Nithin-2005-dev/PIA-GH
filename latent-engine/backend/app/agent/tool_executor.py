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
from app.agent.adapters.successor_adapter import (
    SuccessorAdapter,
)

from app.agent.adapters.transfer_adapter import (
    TransferAdapter,
)


class ToolExecutor:

    def __init__(
        self,
        intelligence_context=None,
    ):

        self._risk = (
            RiskAdapter(
                intelligence_context
            )
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
        
        self._successor = (
            SuccessorAdapter(
                intelligence_context
            )
        )

        self._transfer = (
            TransferAdapter(intelligence_context)
        )

    def execute(
        self,
        intent,
        route,
        context,
    ):

        if route == ToolRoute.RISK:

            summary = (
                self._risk.execute(
                    context
                )
            )

        elif route == ToolRoute.FORECAST:

            summary = (
                self._forecast.execute(
                    context
                )
            )

        elif route == ToolRoute.INTERVENTION:

            summary = (
                self._intervention.execute(
                    context
                )
            )

        elif route == ToolRoute.SUCCESSOR:

            summary = (
                self._successor.execute(
                    context
                )
            )

        elif route == ToolRoute.TRANSFER:

            summary = (
                self._transfer.execute(
                    context
                )
            )

        else:

            summary = (
                self._simulation.execute(
                    context
                )
            )

        return AgentResponse(
            intent=intent.value,
            route=route.value,
            summary=summary,
        )
