import os
from datetime import datetime,UTC

from app.adapters.github.adapter import GitHubAdapter
from app.adapters.github.rest_gateway import GitHubRestGateway

from app.extractor.expertise_extractor import ExpertiseExtractor

from app.estimator.estimation_context import (
    EstimationContext,
)
from app.estimator.expertise_estimator import (
    ExpertiseEstimator,
)
from app.estimator.expertise_projection import (
    ExpertiseProjection,
)
from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)

from app.ports.event_query import EventQuery


def main():

    token = os.environ["GITHUB_TOKEN"]

    gateway = GitHubRestGateway(
        token=token,
    )

    adapter = GitHubAdapter(
        gateway=gateway,
    )

    extractor = ExpertiseExtractor()

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy()
    )

    projection = ExpertiseProjection(
        estimator
    )

    context = EstimationContext(
        current_time=datetime.now(UTC),
        learning_rate=1.0,
        decay_factor=1.0,
    )

    events = adapter.collect(
        EventQuery(
            identifier="facebook/react",
            filters={
                "per_page": 1,
            },
        )
    )

    for event in events:

        evidence_list = extractor.extract(
            event
        )

        for evidence in evidence_list:

            projection.apply(
                evidence,
                context,
            )

    print("\n=== EXPERTISE ESTIMATES ===\n")

    for estimate in projection.all_estimates():

        print(estimate)


if __name__ == "__main__":
    main()