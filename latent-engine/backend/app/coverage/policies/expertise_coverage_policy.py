from collections import defaultdict

from app.coverage.coverage_report import (
    CoverageReport,
)

from .coverage_policy import (
    CoveragePolicy,
)


class ExpertiseCoveragePolicy(
    CoveragePolicy
):

    def _coverage_multiplier(
        self,
        expert_count: int,
    ) -> float:

        if expert_count == 1:
            return 0.50

        if expert_count == 2:
            return 0.75

        if expert_count == 3:
            return 0.90

        return 1.00

    def analyze(
        self,
        expertise_estimates,
    ):

        module_scores = (
            defaultdict(list)
        )

        module_refs = {}

        for estimate in (
            expertise_estimates
        ):

            module_id = (
                estimate
                .module_ref
                .id
            )

            module_scores[
                module_id
            ].append(
                estimate.raw_score
            )

            module_refs[
                module_id
            ] = estimate.module_ref

        reports = []

        for (
            module_id,
            scores,
        ) in module_scores.items():

            expert_count = len(
                scores
            )

            total_expertise = sum(
                scores
            )

            average_expertise = (
                total_expertise
                / expert_count
            )

            coverage_score = (
                average_expertise
                * self._coverage_multiplier(
                    expert_count
                )
            )

            if (
                coverage_score >= 70
            ):
                level = "STRONG"

            elif (
                coverage_score >= 40
            ):
                level = "MODERATE"

            else:
                level = "WEAK"

            reports.append(
                CoverageReport(
                    module_ref=(
                        module_refs[
                            module_id
                        ]
                    ),
                    expert_count=(
                        expert_count
                    ),
                    total_expertise=(
                        total_expertise
                    ),
                    coverage_score=(
                        coverage_score
                    ),
                    coverage_level=(
                        level
                    ),
                )
            )

        reports.sort(
            key=lambda report: (
                report.coverage_score
            ),
            reverse=True,
        )

        return reports