from datetime import UTC
from datetime import datetime
from datetime import timedelta

from app.agent.reasoning_agent import (
    ReasoningAgent,
)

from app.bootstrap.intelligence_context import (
    IntelligenceContext,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.estimator.expertise_estimator import (
    ExpertiseEstimator,
)

from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)

from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)

from app.health.health_report import (
    HealthReport,
)


def module(name):

    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def report(
    module_ref,
    health_score,
):

    return HealthReport(
        module_ref=module_ref,
        health_score=health_score,
        health_level="WARNING",
        coverage_score=50,
        concentration_score=0.75,
        bus_factor=2,
    )


def main():

    #
    # IntelligenceContext still requires
    # an ExpertiseProjection.
    #
    projection = ExpertiseProjection(
        ExpertiseEstimator(
            RuleExpertiseScoringPolicy(),
            ExponentialDecayPolicy(),
        )
    )

    intelligence = IntelligenceContext(
        projection
    )

    payments = module(
        "payments.py"
    )

    now = datetime.now(
        UTC
    )

    #
    # Create declining health history
    #
    scores = [
        95,
        80,
        60,
        40,
    ]

    for index, score in enumerate(
        scores
    ):

        intelligence.health_projection.apply(
            report(
                payments,
                score,
            ),
            now
            - timedelta(
                days=(
                    len(scores)
                    - index
                    - 1
                )
                * 30
            ),
        )

    #
    # Agent
    #
    agent = ReasoningAgent(
        intelligence_context=intelligence
    )

    response = agent.answer(
        "Which modules are deteriorating?"
    )

    print(
        "\n=== FORECAST AGENT ===\n"
    )

    print(
        f"Intent: "
        f"{response.intent}"
    )

    print(
        f"Route: "
        f"{response.route}"
    )

    print()

    print(
        response.summary
    )


if __name__ == "__main__":
    main()