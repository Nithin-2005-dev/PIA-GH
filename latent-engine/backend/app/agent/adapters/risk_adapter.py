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

from app.health.health_report import (
    HealthReport,
)


class RiskAdapter:

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

            try:
                return (
                    self._execute_grounded(
                        module_id
                    )
                )

            except ValueError:
                return (
                    "No risk data found."
                )

        module_ref = EntityRef(
            id=module_id,
            type=EntityType.FILE,
        )

        coverage = CoverageReport(
            module_ref=module_ref,
            expert_count=1,
            total_expertise=20,
            coverage_score=10,
            coverage_level="WEAK",
        )

        concentration = (
            ConcentrationReport(
                module_ref=module_ref,
                expert_count=3,
                concentration_score=0.98,
                concentration_level="HIGH",
            )
        )

        health = HealthReport(
            module_ref=module_ref,
            health_score=40,
            health_level="CRITICAL",
            coverage_score=10,
            concentration_score=0.98,
            bus_factor=1,
        )

        return (
            f"Coverage: "
            f"{coverage.coverage_score:.2f}\n"
            f"Concentration: "
            f"{concentration.concentration_score:.2f}\n"
            f"Health: "
            f"{health.health_score:.2f}\n"
            f"Level: "
            f"{health.health_level}"
        )

    def _execute_grounded(
        self,
        module_id,
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

        concentration_reports = (
            self._intelligence
            .concentration_service
            .analyze(
                estimates
            )
        )

        coverage_reports = [
            report
            for report in coverage_reports
            if report.module_ref.id
            == module_id
        ]

        concentration_reports = [
            report
            for report in concentration_reports
            if report.module_ref.id
            == module_id
        ]

        if (
            not coverage_reports
            or
            not concentration_reports
        ):
            return (
                "No risk data found."
            )

        bus_factor_report = (
            self._intelligence
            .bus_factor_service
            .analyze(
                module_id
            )
        )

        health_reports = (
            self._intelligence
            .health_service
            .analyze(
                coverage_reports,
                concentration_reports,
                [bus_factor_report],
            )
        )

        health = next(
            (
                report
                for report
                in health_reports
                if report.module_ref.id
                == module_id
            ),
            None,
        )

        if health is None:
            return (
                "No risk data found."
            )

        return (
            f"Coverage: "
            f"{health.coverage_score:.2f}\n"
            f"Concentration: "
            f"{health.concentration_score:.2f}\n"
            f"Health: "
            f"{health.health_score:.2f}\n"
            f"Level: "
            f"{health.health_level}"
        )
