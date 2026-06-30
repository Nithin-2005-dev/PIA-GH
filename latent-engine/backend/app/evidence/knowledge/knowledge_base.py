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
                    id="high_risk_maintenance_hotspot",
                    name="High-Risk Maintenance Hotspot",
                    category="maintainability",
                    description=(
                        "Multiple validated measurements indicate that a "
                        "change area is costly and risky to maintain."
                    ),
                    semantic_meaning=(
                        "A localized software area combines high change "
                        "volume, complexity, and review attention need."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="churn-high",
                            measurement_id="code_churn",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=40.0,
                            weight=1.0,
                            explanation="Code churn is high.",
                        ),
                        EvidenceRule(
                            id="complexity-high",
                            measurement_id="patch_complexity_delta",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=2.0,
                            weight=1.0,
                            explanation="Complexity delta is elevated.",
                        ),
                        EvidenceRule(
                            id="review-attention-high",
                            measurement_id="review_attention_need",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.6,
                            weight=0.8,
                            explanation="Review attention need is high.",
                        ),
                    ),
                    required_measurements=(
                        "code_churn",
                        "patch_complexity_delta",
                    ),
                    optional_measurements=(
                        "files_changed",
                        "change_surface_area",
                        "review_attention_need",
                        "change_distribution_entropy",
                    ),
                    synthesis_rules=(
                        "all_required_measurements_present",
                        "weighted_trigger_support",
                        "confidence_weighted_measurement_refs",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                        "semantic",
                        "ontology",
                        "dependency",
                        "benchmark",
                        "confidence",
                        "completeness",
                        "consistency",
                        "contradiction",
                    ),
                    interpretation=(
                        "Treat the affected area as a maintenance hotspot "
                        "until further evidence lowers complexity or churn."
                    ),
                    standards_references=(
                        "ISO/IEC 25010 maintainability",
                        "ISO/IEC 15939 measurement process",
                    ),
                    business_interpretation=(
                        "Sustained work here may require senior review, "
                        "refactoring budget, or ownership reinforcement."
                    ),
                    known_limitations=(
                        "Correlation does not establish causation.",
                        "Static change signals may miss runtime behavior.",
                    ),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.HIGH,
                    rule_reliability=0.88,
                    assumptions=(
                        "Measurements passed the Measurement Layer gate.",
                    ),
                ),
                EvidenceDefinition(
                    id="insufficient_test_signal_risk",
                    name="Insufficient Test Signal Risk",
                    category="testing",
                    description=(
                        "Validated measurements indicate weak verification "
                        "signal relative to change activity."
                    ),
                    semantic_meaning=(
                        "Change activity has insufficient supporting test "
                        "or review confidence."
                    ),
                    triggering_conditions=(
                        EvidenceRule(
                            id="review-attention-medium",
                            measurement_id="review_attention_need",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.7,
                            weight=1.0,
                        ),
                        EvidenceRule(
                            id="surface-area-medium",
                            measurement_id="change_surface_area",
                            operator=EvidenceRuleOperator.GTE,
                            threshold=0.5,
                            weight=0.7,
                        ),
                    ),
                    required_measurements=(
                        "review_attention_need",
                    ),
                    optional_measurements=(
                        "change_surface_area",
                        "files_changed",
                    ),
                    synthesis_rules=(
                        "required_measurement_present",
                        "risk_support_from_optional_measurements",
                    ),
                    confidence_strategy="factor_product_with_explanation",
                    validation_rules=(
                        "logical",
                        "semantic",
                        "ontology",
                        "dependency",
                        "benchmark",
                        "confidence",
                        "completeness",
                        "consistency",
                        "contradiction",
                    ),
                    interpretation=(
                        "Prioritize additional review or targeted tests."
                    ),
                    standards_references=(
                        "ISO/IEC 25010 reliability",
                    ),
                    business_interpretation=(
                        "Weak verification signals can increase defect "
                        "escape and support load."
                    ),
                    known_limitations=(
                        "Absence of direct coverage measurement is not proof "
                        "of absence of testing.",
                    ),
                    version_history=("1.0 initial production rule",),
                    severity=EvidenceSeverity.MEDIUM,
                    rule_reliability=0.78,
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

