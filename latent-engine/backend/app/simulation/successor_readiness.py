from dataclasses import dataclass


@dataclass(frozen=True)
class SuccessorReadiness:

    successor: str

    readiness_score: float