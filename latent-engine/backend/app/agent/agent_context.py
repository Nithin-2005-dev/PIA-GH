from dataclasses import dataclass


@dataclass(frozen=True)
class AgentContext:

    module_id: str | None = None

    developer_id: str | None = None