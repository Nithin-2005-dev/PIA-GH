from .intent_classifier import (
    IntentClassifier,
)

from .question_intent import (
    QuestionIntent,
)

from .tool_route import (
    ToolRoute,
)

from .tool_executor import (
    ToolExecutor,
)


class ReasoningAgent:

    def __init__(self):

        self._classifier = (
            IntentClassifier()
        )

        self._executor = (
            ToolExecutor()
        )

    def answer(
        self,
        question: str,
    ):

        intent = (
            self._classifier
            .classify(question)
        )

        if (
            intent
            ==
            QuestionIntent.RISK
        ):

            route = ToolRoute.RISK

        elif (
            intent
            ==
            QuestionIntent.FORECAST
        ):

            route = (
                ToolRoute.FORECAST
            )

        elif (
            intent
            ==
            QuestionIntent.INTERVENTION
        ):

            route = (
                ToolRoute.INTERVENTION
            )

        else:

            route = (
                ToolRoute.SIMULATION
            )

        return (
            self._executor.execute(
                intent,
                route,
            )
        )