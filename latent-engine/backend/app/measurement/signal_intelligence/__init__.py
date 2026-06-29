from importlib import import_module

_EXPORTS = {
    "ClassificationSource": "app.measurement.signal_intelligence.signal_classifier",
    "DefaultSignalCatalog": "app.measurement.signal_intelligence.signals",
    "MappingCardinality": "app.measurement.signal_intelligence.mapping",
    "MeasurementKnowledgeApi": "app.measurement.query.knowledge_api",
    "SemanticMappingValidator": "app.measurement.signal_intelligence.signal_validation",
    "SemanticSignalClassifier": "app.measurement.signal_intelligence.signal_classifier",
    "SignalClassification": "app.measurement.signal_intelligence.signal_classifier",
    "SignalDefinition": "app.measurement.signal_intelligence.signals",
    "SignalDefinitionValidator": "app.measurement.signal_intelligence.signal_validation",
    "SignalMeasurementMapping": "app.measurement.signal_intelligence.mapping",
    "SignalMeasurementMappingRegistry": "app.measurement.signal_intelligence.mapping",
    "SignalOntology": "app.measurement.signal_intelligence.signal_ontology",
    "SignalOntologyEdge": "app.measurement.signal_intelligence.signal_ontology",
    "SignalOntologyNode": "app.measurement.signal_intelligence.signal_ontology",
    "SignalRegistry": "app.measurement.signal_intelligence.signals",
    "SignalRelationship": "app.measurement.signal_intelligence.signal_ontology",
    "SignalToMeasurementMapper": "app.measurement.signal_intelligence.mapping",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

