from importlib import import_module

_EXPORTS = {
    "ClassificationSource": "app.cognitive.classifiers.signal_classifier",
    "DefaultSignalCatalog": "app.cognitive.classifiers.signals",
    "MappingCardinality": "app.cognitive.classifiers.mapping",
    "MeasurementKnowledgeApi": "app.measurement.query.knowledge_api",
    "SemanticMappingValidator": "app.cognitive.classifiers.signal_validation",
    "SemanticSignalClassifier": "app.cognitive.classifiers.signal_classifier",
    "SignalClassification": "app.cognitive.classifiers.signal_classifier",
    "SignalDefinition": "app.cognitive.classifiers.signals",
    "SignalDefinitionValidator": "app.cognitive.classifiers.signal_validation",
    "SignalMeasurementMapping": "app.cognitive.classifiers.mapping",
    "SignalMeasurementMappingRegistry": "app.cognitive.classifiers.mapping",
    "SignalOntology": "app.cognitive.classifiers.signal_ontology",
    "SignalOntologyEdge": "app.cognitive.classifiers.signal_ontology",
    "SignalOntologyNode": "app.cognitive.classifiers.signal_ontology",
    "SignalRegistry": "app.cognitive.classifiers.signals",
    "SignalRelationship": "app.cognitive.classifiers.signal_ontology",
    "SignalToMeasurementMapper": "app.cognitive.classifiers.mapping",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

