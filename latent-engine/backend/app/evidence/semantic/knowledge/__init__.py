from importlib import import_module

_EXPORTS = {
    "ConceptRelationship": "app.evidence.semantic.knowledge.semantic_graph",
    "DefaultDomainPacks": "app.evidence.semantic.knowledge.domain_packs",
    "DefaultSoftwareMeasurementKnowledge": "app.evidence.semantic.knowledge.measurement_knowledge",
    "MeasurementDefinitionKnowledge": "app.evidence.semantic.knowledge.measurement_knowledge",
    "MeasurementKnowledgeBase": "app.evidence.semantic.knowledge.knowledge_base",
    "MeasurementKnowledgeEntry": "app.evidence.semantic.knowledge.knowledge_base",
    "SemanticMeasurementEdge": "app.evidence.semantic.knowledge.semantic_graph",
    "SemanticMeasurementGraph": "app.evidence.semantic.knowledge.semantic_graph",
    "SoftwareMeasurementKnowledgeBase": "app.evidence.semantic.knowledge.measurement_knowledge",
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

