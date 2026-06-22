from app.ownership.ownership_estimate import (
    OwnershipEstimate,
)

from app.risk.bus_factor import (
    BusFactor,
)

from app.risk.risk_level import (
    RiskLevel,
)

from .bus_factor_policy import (
    BusFactorPolicy,
)


class OwnershipBusFactorPolicy(
    BusFactorPolicy
):

    def __init__(
        self,
        coverage_threshold: float = 0.8,
    ):
        self._coverage_threshold = (
            coverage_threshold
        )

    def calculate(
        self,
        ownership: list[OwnershipEstimate],
    ) -> BusFactor:

        if not ownership:

            raise ValueError(
                "Ownership list cannot be empty."
            )

        sorted_ownership = sorted(
            ownership,
            key=lambda owner: (
                owner.ownership_percentage
            ),
            reverse=True,
        )

        coverage = 0.0

        count = 0

        for owner in sorted_ownership:

            coverage += (
                owner.ownership_percentage
            )

            count += 1

            if (
                coverage
                >= self._coverage_threshold
            ):
                break

        if count == 1:

            risk_level = (
                RiskLevel.HIGH
            )

        elif count == 2:

            risk_level = (
                RiskLevel.MEDIUM
            )

        else:

            risk_level = (
                RiskLevel.LOW
            )

        return BusFactor(
            module_ref=(
                ownership[0].module_ref
            ),
            value=count,
            coverage=coverage,
            risk_level=risk_level,
        )