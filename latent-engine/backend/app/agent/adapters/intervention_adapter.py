from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.coverage.coverage_report import (
    CoverageReport,
)

from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.forecasting.forecast_severity import (
    ForecastSeverity,
)

from app.intervention.intervention_impact_service import (
    InterventionImpactService,
)

from app.intervention.intervention_planner import (
    InterventionPlanner,
)


class InterventionAdapter:

    def __init__(
        self,
        intelligence_context=None,
    ):
        self._intelligence = (
            intelligence_context
        )

    def execute(
        self,
        context,
    ):

        module_id = (
            context.module_id
            or
            "payments.py"
        )

        if (
            self._intelligence
            is not None
        ):

            estimates = (
                self._intelligence
                .projection
                .all_estimates()
            )

            coverage_reports = (
                self._intelligence
                .coverage_service
                .analyze(
                    estimates
                )
            )

            coverage = next(
                report
                for report
                in coverage_reports
                if (
                    report
                    .module_ref
                    .id
                    ==
                    module_id
                )
            )

            concentration_reports = (
                self._intelligence
                .concentration_service
                .analyze(
                    estimates
                )
            )

            concentration = next(
                report
                for report
                in concentration_reports
                if (
                    report
                    .module_ref
                    .id
                    ==
                    module_id
                )
            )

            severities = (
                self._intelligence
                .future_risk_pipeline_service
                .severities(
                    horizon=3
                )
            )

            severity = next(
                item
                for item
                in severities
                if (
                    item
                    .module_ref
                    .id
                    ==
                    module_id
                )
            )

        else:

            module = EntityRef(
                id=module_id,
                type=EntityType.FILE,
            )

            coverage = CoverageReport(
                module_ref=module,
                expert_count=1,
                total_expertise=20,
                coverage_score=10,
                coverage_level="WEAK",
            )

            concentration = (
                ConcentrationReport(
                    module_ref=module,
                    expert_count=3,
                    concentration_score=0.98,
                    concentration_level="HIGH",
                )
            )

            severity = ForecastSeverity(
                module_ref=module,
                current_health=40,
                predicted_health=10,
                severity_score=0.75,
                severity_level="EXTREME",
            )

        interventions = (
            InterventionImpactService()
            .estimate(
                coverage_report=coverage,
                concentration_report=(
                    concentration
                ),
                severity_report=(
                    severity
                ),
            )
        )

        plan = (
            InterventionPlanner()
            .create_plan(
                module_ref=(
                    coverage.module_ref
                ),
                interventions=interventions,
            )
        )

        lines = []

        for index, item in enumerate(
            plan.interventions,
            start=1,
        ):

            lines.append(
                f"{index}. "
                f"{item.action} "
                f"(+{item.expected_health_gain:.2f})"
            )

        lines.append(
            f"Total Expected Gain: "
            f"{plan.total_expected_gain:.2f}"
        )

        return "\n".join(lines)
