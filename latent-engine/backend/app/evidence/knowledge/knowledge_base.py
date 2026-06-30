from app.evidence.domain import EvidenceSeverity
from app.evidence.knowledge.definitions import EvidenceDefinition
from app.evidence.knowledge.definitions import EvidenceRule
from app.evidence.knowledge.definitions import EvidenceRuleOperator


class EvidenceKnowledgeBase:

    def __init__(
        self,
        definitions: tuple[EvidenceDefinition, ...] = (),
    ):
        self._definitions = {
            definition.id: definition
            for definition in definitions
        }

    @classmethod
    def default(
        cls,
    ) -> "EvidenceKnowledgeBase":
        return cls(
            definitions=(
                EvidenceDefinition(
                    id="file_maintenance_risk",
                    name="File Maintenance Risk",
                    category="maintainability",
                    description=(
                        "Hypothesis: File subsystem has elevated maintenance risk "
                        "due to high churn and complexity."
                    ),
                    semantic_meaning=(
                        "A localized software area combines high change "
                        "volume, complexity, and review attention need."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="file-churn-high",
                            measurement_id="file_churn",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=20.0,
                            weight=1.0,
                            explanation="File churn is high.",
                        ),
                        EvidenceRule(
                            id="complexity-high",
                            measurement_id="file_complexity_delta",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=2.0,
                            weight=1.0,
                            explanation="Complexity delta is elevated.",
                        ),
                    ),
                    required_measurements=(
                        "file_churn",
                    ),
                    optional_measurements=(
                        "file_complexity_delta",
                        "file_touch_count",
                    ),
                    synthesis_rules=(
                        "all_required_measurements_present",
                        "weighted_trigger_support",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                        "semantic",
                        "ontology",
                    ),
                    interpretation=(
                        "Treat the affected area as a maintenance hotspot."
                    ),
                    standards_references=(
                        "ISO/IEC 25010 maintainability",
                    ),
                    business_interpretation=(
                        "Sustained work here may require senior review."
                    ),
                    known_limitations=(
                        "Static change signals may miss runtime behavior.",
                    ),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.HIGH,
                    rule_reliability=0.88,
                ),
                EvidenceDefinition(
                    id="developer_broad_knowledge",
                    name="Developer Broad Knowledge",
                    category="knowledge",
                    description=(
                        "Hypothesis: Developer has broad knowledge based on "
                        "touching many distinct files."
                    ),
                    semantic_meaning=(
                        "Developer has interacted with a wide surface area."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="file-touch-high",
                            measurement_id="author_file_touch_count",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=3.0,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=(
                        "author_file_touch_count",
                    ),
                    optional_measurements=(
                        "author_contribution_count",
                        "author_code_churn",
                    ),
                    synthesis_rules=(
                        "required_measurement_present",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                    ),
                    interpretation=(
                        "Developer is expanding system understanding."
                    ),
                    standards_references=(),
                    business_interpretation=(
                        "Valuable for cross-team reviews."
                    ),
                    known_limitations=(),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=0.8,
                ),
                EvidenceDefinition(
                    id="developer_high_velocity",
                    name="Developer High Velocity",
                    category="activity",
                    description=(
                        "Hypothesis: Developer is producing changes at a high rate."
                    ),
                    semantic_meaning=(
                        "Developer has frequent contributions."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="contribution-high",
                            measurement_id="author_contribution_count",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=2.0,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=(
                        "author_contribution_count",
                    ),
                    optional_measurements=(
                        "author_code_churn",
                    ),
                    synthesis_rules=(
                        "required_measurement_present",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                    ),
                    interpretation=(
                        "Developer is actively shipping code."
                    ),
                    standards_references=(),
                    business_interpretation=(
                        "High throughput contributor."
                    ),
                    known_limitations=(),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.LOW,
                    rule_reliability=0.9,
                ),
                EvidenceDefinition(
                    id="subsystem_high_churn",
                    name="Subsystem High Churn",
                    category="volatility",
                    description=(
                        "Hypothesis: Subsystem is undergoing significant changes."
                    ),
                    semantic_meaning=(
                        "Directory has high volume of modifications."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="dir-churn-high",
                            measurement_id="directory_churn",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=100.0,
                            weight=1.0,
                        ),
                    ),
                    required_measurements=(
                        "directory_churn",
                    ),
                    optional_measurements=(
                        "directory_file_count",
                    ),
                    synthesis_rules=(
                        "required_measurement_present",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                    ),
                    interpretation=(
                        "Subsystem is highly volatile."
                    ),
                    standards_references=(),
                    business_interpretation=(
                        "May need stabilization."
                    ),
                    known_limitations=(),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.85,
                ),
            )
        )

    def register(
        self,
        definition: EvidenceDefinition,
    ) -> None:
        self._definitions[
            definition.id
        ] = definition

    def get(
        self,
        definition_id: str,
    ) -> EvidenceDefinition:
        return self._definitions[
            definition_id
        ]

    def all(
        self,
    ) -> tuple[EvidenceDefinition, ...]:
        return tuple(
            self._definitions.values()
        )
