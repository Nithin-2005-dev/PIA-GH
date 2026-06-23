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

    def execute(self):

        module = EntityRef(
            id="payments.py",
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
                module_ref=module,
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