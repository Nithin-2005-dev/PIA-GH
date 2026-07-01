from app.temporal.models import HistoricalContext
from .models import TimeSeries, TimeSeriesPoint


class TimeSeriesFactory:
    """
    Extracts generic TimeSeries sequences from the HistoricalContext.
    This decouples the ForecastEngine from the snapshot schema.
    """

    @staticmethod
    def build_observations_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            points.append(
                TimeSeriesPoint(
                    snapshot_id=snap.snapshot_id,
                    timestamp=snap.timestamp,
                    value=float(snap.observation_count)
                )
            )
        return TimeSeries(metric_name="observations", points=tuple(points))

    @staticmethod
    def build_health_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            if snap.org_health is not None:
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=snap.snapshot_id,
                        timestamp=snap.timestamp,
                        value=float(snap.org_health.average_health)
                    )
                )
        return TimeSeries(metric_name="health", points=tuple(points))

    @staticmethod
    def build_bus_factor_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            if snap.org_health is not None:
                # Average bus factor for the org
                value = snap.org_health.average_bus_factor if hasattr(snap.org_health, "average_bus_factor") else 1.0
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=snap.snapshot_id,
                        timestamp=snap.timestamp,
                        value=float(value)
                    )
                )
        return TimeSeries(metric_name="bus_factor", points=tuple(points))

    @staticmethod
    def build_knowledge_risk_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            if snap.org_health is not None:
                value = snap.org_health.knowledge_risk if hasattr(snap.org_health, "knowledge_risk") else 0.0
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=snap.snapshot_id,
                        timestamp=snap.timestamp,
                        value=float(value)
                    )
                )
        return TimeSeries(metric_name="knowledge_risk", points=tuple(points))

    @staticmethod
    def build_coverage_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            if snap.org_health is not None:
                value = snap.org_health.average_coverage if hasattr(snap.org_health, "average_coverage") else 0.0
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=snap.snapshot_id,
                        timestamp=snap.timestamp,
                        value=float(value)
                    )
                )
        return TimeSeries(metric_name="coverage", points=tuple(points))

    @staticmethod
    def build_expertise_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            points.append(
                TimeSeriesPoint(
                    snapshot_id=snap.snapshot_id,
                    timestamp=snap.timestamp,
                    value=float(snap.expertise_count)
                )
            )
        return TimeSeries(metric_name="expertise", points=tuple(points))

    @staticmethod
    def build_knowledge_growth_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            points.append(
                TimeSeriesPoint(
                    snapshot_id=snap.snapshot_id,
                    timestamp=snap.timestamp,
                    value=float(snap.knowledge_count)
                )
            )
        return TimeSeries(metric_name="knowledge_growth", points=tuple(points))

    @staticmethod
    def build_ownership_concentration_series(history: HistoricalContext) -> TimeSeries[float]:
        points = []
        for snap in history.snapshots:
            if snap.org_health is not None:
                value = snap.org_health.concentration if hasattr(snap.org_health, "concentration") else 0.0
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=snap.snapshot_id,
                        timestamp=snap.timestamp,
                        value=float(value)
                    )
                )
        return TimeSeries(metric_name="ownership_concentration", points=tuple(points))

    @classmethod
    def build_all(cls, history: HistoricalContext) -> dict[str, TimeSeries[float]]:
        return {
            "observations": cls.build_observations_series(history),
            "health": cls.build_health_series(history),
            "bus_factor": cls.build_bus_factor_series(history),
            "knowledge_risk": cls.build_knowledge_risk_series(history),
            "coverage": cls.build_coverage_series(history),
            "expertise": cls.build_expertise_series(history),
            "knowledge_growth": cls.build_knowledge_growth_series(history),
            "ownership_concentration": cls.build_ownership_concentration_series(history),
        }
