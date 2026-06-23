from dataclasses import dataclass


@dataclass(frozen=True)
class AgentResponse:

    intent: str

    route: str

    summary: str