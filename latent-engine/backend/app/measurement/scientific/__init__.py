from importlib import import_module

_EXPORTS = {
    "AccuracyProfileRegistry": "app.measurement.scientific.accuracy_profiles",
    "CatalogValidationService": "app.measurement.scientific.scientific_validation",
    "ConfidenceCalibrationModel": "app.measurement.scientific.confidence_calibration",
    "ConfidenceCalibrationReport": "app.measurement.scientific.confidence_calibration",
    "ConfidenceObservation": "app.measurement.scientific.confidence_calibration",
    "EnterpriseMeasurementCatalog": "app.measurement.scientific.scientific_catalog",
    "ExpectedMeasurement": "app.measurement.scientific.test_corpus",
    "MeasurementAccuracyProfile": "app.measurement.scientific.accuracy_profiles",
    "MeasurementTestCorpus": "app.measurement.scientific.test_corpus",
    "MeasurementTestDataset": "app.measurement.scientific.test_corpus",
    "ScientificMeasurementApi": "app.measurement.scientific.scientific_api",
    "ScientificMeasurementSpec": "app.measurement.scientific.scientific_catalog",
    "ScientificValidationEngine": "app.measurement.scientific.scientific_validation",
    "ScientificValidationReport": "app.measurement.scientific.scientific_validation",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

