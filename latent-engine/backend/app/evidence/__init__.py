from importlib import import_module
import sys

_LEGACY_MODULE_ALIASES = {
    "conflicts": "app.evidence.correlation.conflicts",
    "eql": "app.evidence.query.eql",
    "knowledge_base": "app.evidence.knowledge.knowledge_base",
}

for _legacy_name, _target_name in _LEGACY_MODULE_ALIASES.items():
    sys.modules[f"{__name__}.{_legacy_name}"] = import_module(
        _target_name
    )

from app.evidence.api import EvidenceApi
from app.evidence.correlation import EvidenceConflictEngine
from app.evidence.correlation import EvidenceCorrelationEngine
from app.evidence.core import EvidenceContext
from app.evidence.core import EvidencePackage
from app.evidence.domain import Evidence
from app.evidence.domain import EvidenceLifecycle
from app.evidence.domain import EvidencePriority
from app.evidence.domain import EvidenceSeverity
from app.evidence.graph import EvidenceKnowledgeGraph
from app.evidence.knowledge import EvidenceDefinition
from app.evidence.knowledge import EvidenceKnowledgeBase
from app.evidence.ontology import EvidenceOntology
from app.evidence.query import EqlEngine
from app.evidence.query import EqlParser
from app.evidence.ranking import EvidenceRankingEngine
from app.evidence.streaming import StreamingEvidenceEngine
from app.evidence.synthesis import EvidenceSynthesisEngine

__all__ = [
    "EqlEngine",
    "EqlParser",
    "Evidence",
    "EvidenceApi",
    "EvidenceConflictEngine",
    "EvidenceContext",
    "EvidenceCorrelationEngine",
    "EvidenceDefinition",
    "EvidenceKnowledgeGraph",
    "EvidenceKnowledgeBase",
    "EvidenceLifecycle",
    "EvidenceOntology",
    "EvidencePackage",
    "EvidencePriority",
    "EvidenceRankingEngine",
    "EvidenceSeverity",
    "EvidenceSynthesisEngine",
    "StreamingEvidenceEngine",
]
