from app.health.health_report import (
    HealthReport,
)

from .health_policy import (
    HealthPolicy,
)


class OrganizationalHealthPolicy(
    HealthPolicy
):

    def _bus_factor_health(
        self,
        bus_factor: int,
    ) -> float:

        if bus_factor >= 4:
            return 100.0

        if bus_factor == 3:
            return 75.0

        if bus_factor == 2:
            return 50.0

        return 25.0

    def evaluate(
        self,
        coverage_reports,
        concentration_reports,
        bus_factor_reports,
    ):

        concentration_by_module = {
            report.module_ref.id: report
            for report in concentration_reports
        }

        bus_factor_by_module = {
            report.module_ref.id: report
            for report in bus_factor_reports
        }

        reports = []

        for coverage in coverage_reports:

            module_id = (
                coverage.module_ref.id
            )

            concentration = (
                concentration_by_module[
                    module_id
                ]
            )

            bus_factor = (
                bus_factor_by_module[
                    module_id
                ]
            )

            concentration_health = (
                1
                - concentration
                .concentration_score
            ) * 100

            bus_health = (
                self._bus_factor_health(
                    bus_factor.value
                )
            )

            health_score = (

                0.4
                * coverage.coverage_score

                +

                0.4
                * concentration_health

                +

                0.2
                * bus_health
            )

            if health_score >= 75:

                level = "HEALTHY"

            elif health_score >= 50:

                level = "WARNING"

            else:

                level = "CRITICAL"

            reports.append(
                HealthReport(
                    module_ref=(
                        coverage.module_ref
                    ),
                    health_score=(
                        health_score
                    ),
                    health_level=(
                        level
                    ),
                    coverage_score=(
                        coverage.coverage_score
                    ),
                    concentration_score=(
                        concentration
                        .concentration_score
                    ),
                    bus_factor=(
                        bus_factor
                        .value
                    ),
                )
            )

        reports.sort(
            key=lambda report: (
                report.health_score
            ),
            reverse=True,
        )

        return reports