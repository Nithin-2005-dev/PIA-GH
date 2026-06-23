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
        
        if (
        "take over" in question
        or
        "successor" in question
        or
        "replace" in question
        ):
            return (
            QuestionIntent.SUCCESSOR
        )

        if (

            "knowledge transfer" in question

            or "transfer plan" in question

            or "invest knowledge" in question

            or "train" in question

            or "mentor" in question

            or "learn" in question

        ):
            return (
                QuestionIntent.TRANSFER
            )

        return (
            QuestionIntent.RISK
        )