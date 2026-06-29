from importlib import import_module

_EXPORTS = {
    "ActiveMeasurementService": "app.measurement.core.active",
    "CostBasedMeasurementOptimizer": "app.measurement.core.execution",
    "EnterpriseAccuracyPipeline": "app.measurement.core.accuracy",
    "MeasurementCache": "app.measurement.core.store",
    "MeasurementComputationNode": "app.measurement.core.execution",
    "MeasurementDependencyGraph": "app.measurement.core.recompute",
    "MeasurementEngine": "app.measurement.core.engine",
    "MeasurementExecutionPlanner": "app.measurement.core.execution",
    "MeasurementExecutor": "app.measurement.core.execution",
    "NormalizationPipeline": "app.measurement.core.normalization_pipeline",
    "StreamingMeasurementEngine": "app.measurement.core.streaming",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

