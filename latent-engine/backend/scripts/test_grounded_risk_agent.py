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

    agent = ReasoningAgent(
        intelligence_context=intelligence
    )

    response = agent.answer(
        "Why is auth.py risky?"
    )

    print(
        response.summary
    )


if __name__ == "__main__":
    main()
