from enum import Enum


class ToolRoute(
    str,
    Enum,
):

    RISK = "Risk Analysis"

    FORECAST = "Forecast Analysis"

    INTERVENTION = (
        "Intervention Planning"
    )

    SIMULATION = (
        "Simulation Engine"
    )
    
    SUCCESSOR = (
    "Successor Recommendation"
)

    TRANSFER = (
        "Knowledge Transfer"
    )