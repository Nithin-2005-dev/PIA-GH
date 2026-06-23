from enum import Enum


class QuestionIntent(
    str,
    Enum,
):

    RISK = "RISK"

    FORECAST = "FORECAST"

    INTERVENTION = "INTERVENTION"

    SIMULATION = "SIMULATION"