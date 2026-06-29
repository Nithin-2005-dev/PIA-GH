from importlib import import_module

_EXPORTS = {
    "DriftDetectionEngine": "app.measurement.analytics.drift",
    "DriftResult": "app.measurement.analytics.drift",
    "GraphMeasurementEngine": "app.measurement.analytics.graph",
    "GraphMeasurementResult": "app.measurement.analytics.graph",
    "OutlierDetectionEngine": "app.measurement.analytics.outliers",
    "StatisticalEngine": "app.measurement.analytics.statistical",
    "StatisticalReport": "app.measurement.analytics.statistical_pipeline",
    "StatisticsPipeline": "app.measurement.analytics.statistical_pipeline",
    "TimeSeriesMeasurementEngine": "app.measurement.analytics.time_series",
    "TrendEstimate": "app.measurement.analytics.time_series",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

