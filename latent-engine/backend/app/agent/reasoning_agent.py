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

from .context_extractor import (
    ContextExtractor,
)


class ReasoningAgent:

    def __init__(
        self,
        intelligence_context=None,
    ):

        self._classifier = (
            IntentClassifier()
        )

        self._executor = (
            ToolExecutor(
                intelligence_context
            )
        )
        self._context_extractor = (
            ContextExtractor()
        )

    def answer(
        self,
        question: str,
    ):

        intent = (
            self._classifier
            .classify(question)
        )
        context = (
            self._context_extractor
            .extract(question)
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
        elif (
            intent
            ==
            QuestionIntent.SUCCESSOR
        ):

            route = (
                ToolRoute.SUCCESSOR
            )
        elif (
            intent
            ==
            QuestionIntent.TRANSFER
        ):

            route = (
                ToolRoute.TRANSFER
            )
        else:

            route = (
                ToolRoute.SIMULATION
            )
        
        return (
            self._executor.execute(
                intent,
                route,
                context,
            )
        )
