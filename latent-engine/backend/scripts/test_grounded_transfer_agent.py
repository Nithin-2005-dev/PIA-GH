from datetime import UTC
from datetime import datetime
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


def main():

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(),
    )

    projection = ExpertiseProjection(
        estimator
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

    print(
        "\n=== DEBUG ===\n"
    )

    reports = (
        intelligence
        .concentration_service
        .analyze(
            projection.all_estimates()
        )
    )

    for report in reports:

        print(
            f"Module: {report.module_ref.id}"
        )

        print(
            f"Score: {report.concentration_score:.2f}"
        )

        print(
            f"Level: {report.concentration_level}"
        )

        print(
            "-" * 60
        )

    ownerships = (
        intelligence
        .ownership_service
        .owners_of(
            "auth.py"
        )
    )

    print(
        f"Owners: {len(ownerships)}"
    )

    successors = (
        intelligence
        .successor_service
        .recommend(
            "auth.py"
        )
    )

    print(
        f"Successors: {len(successors)}"
    )

    print(
        "\n=== AGENT ===\n"
    )

    agent = ReasoningAgent(
        intelligence_context=intelligence
    )

    response = agent.answer(
        "Which developer should we train for auth.py?"
    )

    print(
        response.summary
    )
    print("\n=== OWNERSHIP ===\n")

    for owner in ownerships:

        print(
            owner.owner_ref.id,
            owner.ownership_percentage,
            owner.effective_score,
            owner.ownership_level,
        )


if __name__ == "__main__":
    main()