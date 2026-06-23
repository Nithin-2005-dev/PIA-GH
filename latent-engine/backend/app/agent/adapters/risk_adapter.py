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

        health = HealthReport(
            module_ref=module,
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