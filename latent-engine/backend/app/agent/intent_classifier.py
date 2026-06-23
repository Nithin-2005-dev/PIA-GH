from .question_intent import (
    QuestionIntent,
)


class IntentClassifier:

    def classify(
        self,
        question: str,
    ):

        question = (
            question.lower()
        )

        if (
            "improve" in question
            or
            "recommend" in question
            or
            "action" in question
        ):

            return (
                QuestionIntent.INTERVENTION
            )

        if (
            "leave" in question
            or
            "departure" in question
            or
            "what if" in question
        ):

            return (
                QuestionIntent.SIMULATION
            )

        if (
            "forecast" in question
            or
            "future" in question
            or
            "deteriorating" in question
        ):

            return (
                QuestionIntent.FORECAST
            )

        return (
            QuestionIntent.RISK
        )