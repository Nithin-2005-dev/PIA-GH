from app.evidence.core import EvidenceContext
from app.evidence.core import EvidencePackage
from app.evidence.domain import Evidence
from app.evidence.graph import EvidenceKnowledgeGraph
from app.evidence.query import EqlEngine
from app.evidence.query import EqlParser
from app.evidence.ranking import EvidenceRankingEngine
from app.evidence.synthesis import EvidenceSynthesisEngine
from app.measurement.domain import Measurement


class EvidenceApi:

    def __init__(
        self,
        synthesis_engine: EvidenceSynthesisEngine | None = None,
        ranking_engine: EvidenceRankingEngine | None = None,
    ):
        self._synthesis_engine = (
            synthesis_engine
            or EvidenceSynthesisEngine()
        )
        self._ranking_engine = (
            ranking_engine
            or EvidenceRankingEngine()
        )
        self._packages: dict[str, EvidencePackage] = {}

    def generate(
        self,
        measurements: list[Measurement],
        context: EvidenceContext,
    ) -> EvidencePackage:
        package = self._synthesis_engine.synthesize(
            measurements,
            context,
        )
        self._packages[
            self._key(
                context.tenant_id
            )
        ] = package
        return package

    def lookup(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> Evidence:
        for evidence in self._package(
            tenant_id
        ).evidence:
            if evidence.evidence_id == evidence_id:
                return evidence
        raise KeyError(
            evidence_id
        )

    def search(
        self,
        eql: str,
        tenant_id: str | None = None,
    ) -> tuple[Evidence, ...]:
        query = EqlParser().parse(
            eql
        )
        return EqlEngine().query(
            self._package(
                tenant_id
            ).evidence,
            query,
        )

    def explanation(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> dict[str, object]:
        evidence = self.lookup(
            evidence_id,
            tenant_id,
        )
        return {
            "id": evidence.evidence_id,
            "name": evidence.name,
            "confidence": evidence.confidence,
            "confidence_factors": (
                evidence.traceability.confidence_factors
            ),
            "explanation": evidence.traceability.explanation,
            "supporting_measurements": [
                measurement.definition_id
                for measurement in evidence.supporting_measurements
            ],
            "assumptions": evidence.assumptions,
            "limitations": evidence.limitations,
            "validation": [
                result.status.value
                for result in evidence.validation_results
            ],
        }

    def lineage(
        self,
        evidence_id: str,
        tenant_id: str | None = None,
    ) -> tuple[str, ...]:
        evidence = self.lookup(
            evidence_id,
            tenant_id,
        )
        return evidence.lineage.source_measurement_ids

    def graph(
        self,
        tenant_id: str | None = None,
    ) -> EvidenceKnowledgeGraph:
        graph = EvidenceKnowledgeGraph()
        for evidence in self._package(
            tenant_id
        ).evidence:
            graph.add_evidence(
                evidence
            )
        return graph

    def compare(
        self,
        left_id: str,
        right_id: str,
        tenant_id: str | None = None,
    ) -> dict[str, object]:
        left = self.lookup(
            left_id,
            tenant_id,
        )
        right = self.lookup(
            right_id,
            tenant_id,
        )
        return {
            "confidence_delta": left.confidence - right.confidence,
            "severity_delta": (
                left.severity.rank()
                - right.severity.rank()
            ),
            "shared_measurements": tuple(
                set(
                    left.lineage.source_measurement_ids
                ).intersection(
                    right.lineage.source_measurement_ids
                )
            ),
        }

    def export(
        self,
        tenant_id: str | None = None,
    ) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                "id": evidence.evidence_id,
                "name": evidence.name,
                "category": evidence.category,
                "confidence": evidence.confidence,
                "severity": evidence.severity.value,
                "priority": evidence.priority.value,
                "measurements": (
                    evidence.lineage.source_measurement_ids
                ),
            }
            for evidence in self._ranking_engine.rank(
                self._package(
                    tenant_id
                ).evidence
            )
        )

    def _package(
        self,
        tenant_id: str | None,
    ) -> EvidencePackage:
        return self._packages[
            self._key(
                tenant_id
            )
        ]

    def _key(
        self,
        tenant_id: str | None,
    ) -> str:
        return tenant_id or "global"

