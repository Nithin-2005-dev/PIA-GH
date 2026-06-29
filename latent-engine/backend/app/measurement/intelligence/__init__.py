from importlib import import_module

_EXPORTS = {
    "ConceptRelationship": "app.measurement.intelligence.semantic_graph",
    "DefaultDomainPacks": "app.measurement.intelligence.domain_packs",
    "DefaultSoftwareMeasurementKnowledge": "app.measurement.intelligence.measurement_knowledge",
    "MeasurementDefinitionKnowledge": "app.measurement.intelligence.measurement_knowledge",
    "MeasurementKnowledgeBase": "app.measurement.intelligence.knowledge_base",
    "MeasurementKnowledgeEntry": "app.measurement.intelligence.knowledge_base",
    "SemanticMeasurementEdge": "app.measurement.intelligence.semantic_graph",
    "SemanticMeasurementGraph": "app.measurement.intelligence.semantic_graph",
    "SoftwareMeasurementKnowledgeBase": "app.measurement.intelligence.measurement_knowledge",
    "StandardReference": "app.measurement.scientific.standards",
    "StandardsCatalog": "app.measurement.scientific.standards",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

