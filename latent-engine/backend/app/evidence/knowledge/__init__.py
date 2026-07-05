from importlib import import_module

_EXPORTS = {
    "ConceptRelationship": "app.evidence.knowledge.semantic_graph",
    "DefaultDomainPacks": "app.evidence.knowledge.domain_packs",
    "DefaultSoftwareMeasurementKnowledge": "app.evidence.knowledge.measurement_knowledge",
    "MeasurementDefinitionKnowledge": "app.evidence.knowledge.measurement_knowledge",
    "EvidenceDefinition": "app.evidence.knowledge.definitions",
    "EvidenceRule": "app.evidence.knowledge.definitions",
    "EvidenceRuleOperator": "app.evidence.knowledge.definitions",
    "EvidenceKnowledgeBase": "app.evidence.knowledge.knowledge_base",
    "MeasurementKnowledgeBase": "app.evidence.knowledge.knowledge_base",
    "MeasurementKnowledgeEntry": "app.evidence.knowledge.knowledge_base",
    "SemanticMeasurementEdge": "app.evidence.knowledge.semantic_graph",
    "SemanticMeasurementGraph": "app.evidence.knowledge.semantic_graph",
    "SoftwareMeasurementKnowledgeBase": "app.evidence.knowledge.measurement_knowledge",
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

