import re

from .agent_context import (
    AgentContext,
)


class ContextExtractor:

    def extract(
        self,
        question: str,
    ) -> AgentContext:

        module_match = re.search(
            r"([a-zA-Z0-9_]+\.py)",
            question,
        )

        module_id = None

        if module_match:
            module_id = (
                module_match.group(1)
            )

        developer_id = None

        lower = question.lower()

        if "alice" in lower:
            developer_id = "alice"

        elif "bob" in lower:
            developer_id = "bob"

        elif "charlie" in lower:
            developer_id = "charlie"

        elif "david" in lower:
            developer_id = "david"

        return AgentContext(
            module_id=module_id,
            developer_id=developer_id,
        )