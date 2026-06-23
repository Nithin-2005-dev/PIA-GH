from .health_history import (
    HealthHistory,
)

from .health_trend import (
    HealthTrend,
)

from .trend_direction import (
    TrendDirection,
)


class TrendAnalyzer:

    def analyze(
        self,
        history: HealthHistory,
    ):

        snapshots = sorted(
            history.snapshots,
            key=lambda snapshot: (
                snapshot.recorded_at
            )
        )

        if len(snapshots) < 2:

            raise ValueError(
                "At least two snapshots required."
            )

        first = snapshots[0]

        last = snapshots[-1]

        delta = (
            last.health_score
            - first.health_score
        )

        slope = (
            delta
            /
            (
                len(snapshots) - 1
            )
        )

        if slope > 2:

            direction = (
                TrendDirection.IMPROVING
            )

        elif slope < -2:

            direction = (
                TrendDirection.DECLINING
            )

        else:

            direction = (
                TrendDirection.STABLE
            )

        return HealthTrend(
        module_ref=(
            history.module_ref
        ),
        previous_score=(
            first.health_score
        ),
        current_score=(
            last.health_score
        ),
        delta=delta,
        slope=slope,
        direction=direction,
    )