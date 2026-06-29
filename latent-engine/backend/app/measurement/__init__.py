from importlib import import_module
import sys

_LEGACY_MODULE_ALIASES = {
    'accuracy': 'app.measurement.core.accuracy',
    'active': 'app.measurement.core.active',
    'audit': 'app.measurement.core.audit',
    'composite': 'app.measurement.core.composite',
    'confidence': 'app.measurement.core.confidence',
    'engine': 'app.measurement.core.engine',
    'execution': 'app.measurement.core.execution',
    'formula': 'app.measurement.core.formula',
    'fusion': 'app.measurement.core.fusion',
    'ids': 'app.measurement.core.ids',
    'interfaces': 'app.measurement.core.interfaces',
    'normalization': 'app.measurement.core.normalization',
    'normalization_pipeline': 'app.measurement.core.normalization_pipeline',
    'quality': 'app.measurement.core.quality',
    'recompute': 'app.measurement.core.recompute',
    'store': 'app.measurement.core.store',
    'streaming': 'app.measurement.core.streaming',
    'validation': 'app.measurement.core.validation',
    'catalog': 'app.measurement.domain.catalog',
    'contracts': 'app.measurement.domain.contracts',
    'ontology': 'app.measurement.domain.ontology',
    'registry': 'app.measurement.domain.registry',
    'signals': 'app.measurement.signal_intelligence.signals',
    'signal_ontology': 'app.measurement.signal_intelligence.signal_ontology',
    'signal_classifier': 'app.measurement.signal_intelligence.signal_classifier',
    'mapping': 'app.measurement.signal_intelligence.mapping',
    'signal_validation': 'app.measurement.signal_intelligence.signal_validation',
    'scientific_api': 'app.measurement.scientific.scientific_api',
    'scientific_catalog': 'app.measurement.scientific.scientific_catalog',
    'scientific_validation': 'app.measurement.scientific.scientific_validation',
    'accuracy_profiles': 'app.measurement.scientific.accuracy_profiles',
    'confidence_calibration': 'app.measurement.scientific.confidence_calibration',
    'test_corpus': 'app.measurement.scientific.test_corpus',
    'standards': 'app.measurement.scientific.standards',
    'benchmark': 'app.measurement.benchmarks.benchmark',
    'benchmark_datasets': 'app.measurement.benchmarks.benchmark_datasets',
    'statistical': 'app.measurement.analytics.statistical',
    'statistical_pipeline': 'app.measurement.analytics.statistical_pipeline',
    'graph': 'app.measurement.analytics.graph',
    'time_series': 'app.measurement.analytics.time_series',
    'drift': 'app.measurement.analytics.drift',
    'outliers': 'app.measurement.analytics.outliers',
    'compression': 'app.measurement.analytics.compression',
    'mql': 'app.measurement.query.mql',
    'lineage': 'app.measurement.query.lineage',
    'lineage_query': 'app.measurement.query.lineage_query',
    'knowledge_api': 'app.measurement.query.knowledge_api',
    'knowledge_base': 'app.measurement.intelligence.knowledge_base',
    'measurement_knowledge': 'app.measurement.intelligence.measurement_knowledge',
    'domain_packs': 'app.measurement.intelligence.domain_packs',
    'semantic_graph': 'app.measurement.intelligence.semantic_graph',
    'packs': 'app.measurement.plugins_runtime.packs',
    'plugins': 'app.measurement.plugins_runtime.plugins',
    'ml': 'app.measurement.plugins_runtime.ml',
    'dsl': 'app.measurement.plugins_runtime.dsl',
}

for _legacy_name, _target_name in _LEGACY_MODULE_ALIASES.items():
    sys.modules[f'{__name__}.{_legacy_name}'] = import_module(_target_name)

from app.measurement.core.accuracy import EnterpriseAccuracyPipeline
from app.measurement.domain.catalog import DefaultMeasurementCatalog
from app.measurement.domain.contracts import MeasurementContract, MeasurementLifecycle
from app.measurement.domain import (
    Measurement,
    MeasurementContext,
    MeasurementConcept,
    MeasurementDefinition,
    MeasurementUnit,
)
from app.measurement.core.engine import MeasurementEngine
from app.measurement.core.execution import MeasurementExecutionPlanner
from app.measurement.signal_intelligence.mapping import SignalToMeasurementMapper
from app.measurement.domain.ontology import MeasurementOntology
from app.measurement.domain.registry import MeasurementRegistry
from app.measurement.scientific.scientific_api import ScientificMeasurementApi
from app.measurement.scientific.scientific_catalog import EnterpriseMeasurementCatalog
from app.measurement.scientific.scientific_validation import ScientificValidationEngine
from app.measurement.intelligence.semantic_graph import SemanticMeasurementGraph
from app.measurement.signal_intelligence.signal_classifier import SemanticSignalClassifier
from app.measurement.signal_intelligence.signal_ontology import SignalOntology
from app.measurement.signal_intelligence.signals import DefaultSignalCatalog, SignalRegistry

__all__ = [
    'DefaultMeasurementCatalog',
    'DefaultSignalCatalog',
    'EnterpriseAccuracyPipeline',
    'EnterpriseMeasurementCatalog',
    'Measurement',
    'MeasurementContract',
    'MeasurementConcept',
    'MeasurementContext',
    'MeasurementDefinition',
    'MeasurementEngine',
    'MeasurementExecutionPlanner',
    'MeasurementLifecycle',
    'MeasurementOntology',
    'MeasurementRegistry',
    'MeasurementUnit',
    'SemanticMeasurementGraph',
    'SemanticSignalClassifier',
    'SignalOntology',
    'SignalRegistry',
    'SignalToMeasurementMapper',
    'ScientificMeasurementApi',
    'ScientificValidationEngine',
]
