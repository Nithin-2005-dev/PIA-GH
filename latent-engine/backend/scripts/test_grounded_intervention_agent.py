from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

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

from app.domain.evidence import (
    Evidence,
)

from app.domain.predicate_type import (
    PredicateType,
)

from app.estimator.estimation_context import (
    EstimationContext,
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


def developer(name):

    return EntityRef(
        id=name,
        type=EntityType.DEVELOPER,
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
    # Build intelligence with:
    #   auth.py
    #   alice    95
    #   bob      3
    #   charlie  2
    #
    projection = ExpertiseProjection(
        ExpertiseEstimator(
            RuleExpertiseScoringPolicy(),
            ExponentialDecayPolicy(),
        )
    )

    context = EstimationContext(
        current_time=datetime.now(
            UTC
        ),
        learning_rate=1.0,
    )

    evidence_list = [

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "alice"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "auth.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 95.0,
            },
        ),

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "bob"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "auth.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 3.0,
            },
        ),

        Evidence(
            id=uuid4(),
            source_event_id=uuid4(),
            subject_ref=developer(
                "charlie"
            ),
            predicate=(
                PredicateType.MODIFIED
            ),
            object_ref=module(
                "auth.py"
            ),
            confidence=1.0,
            metadata={
                "strength": 2.0,
            },
        ),
    ]

    for evidence in evidence_list:

        projection.apply(
            evidence,
            context,
        )

    intelligence = IntelligenceContext(
        projection
    )

    #
    # Seed declining health history:
    #   95 → 80 → 60 → 40
    #
    auth_module = module(
        "auth.py"
    )

    now = datetime.now(
        UTC
    )

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
                auth_module,
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
        "How can we improve auth.py?"
    )

    print(
        "\n=== GROUNDED INTERVENTION AGENT ===\n"
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

    #
    # Debug: show what the intelligence services produced
    #
    print(
        "\n=== DEBUG ===\n"
    )

    estimates = (
        projection.all_estimates()
    )

    coverage_reports = (
        intelligence.coverage_service
        .analyze(
            estimates
        )
    )

    print(
        "Coverage Reports:"
    )

    for report_item in coverage_reports:

        print(
            f"  {report_item.module_ref.id}: "
            f"score={report_item.coverage_score:.2f}, "
            f"level={report_item.coverage_level}, "
            f"experts={report_item.expert_count}"
        )

    concentration_reports = (
        intelligence.concentration_service
        .analyze(
            estimates
        )
    )

    print(
        "Concentration Reports:"
    )

    for report_item in concentration_reports:

        print(
            f"  {report_item.module_ref.id}: "
            f"score={report_item.concentration_score:.2f}, "
            f"level={report_item.concentration_level}"
        )

    severities = (
        intelligence.future_risk_pipeline_service
        .severities(
            horizon=3
        )
    )

    print(
        "Forecast Severities:"
    )

    for item in severities:

        print(
            f"  {item.module_ref.id}: "
            f"current={item.current_health}, "
            f"predicted={item.predicted_health}, "
            f"severity={item.severity_score:.2f}, "
            f"level={item.severity_level}"
        )


if __name__ == "__main__":
    main()
