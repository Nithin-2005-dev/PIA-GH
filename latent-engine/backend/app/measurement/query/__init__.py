from importlib import import_module

_EXPORTS = {
    "MeasurementExplainer": "app.measurement.query.lineage",
    "MeasurementLineageGraph": "app.measurement.query.lineage",
    "MeasurementLineageQueryEngine": "app.measurement.query.lineage_query",
    "MeasurementLineageService": "app.measurement.query.lineage",
    "MqlEngine": "app.measurement.query.mql",
    "MqlParser": "app.measurement.query.mql",
    "MqlQuery": "app.measurement.query.mql",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

