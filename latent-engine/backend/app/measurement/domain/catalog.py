from app.measurement.domain import ExpectedRange
from app.measurement.domain import MeasurementDefinition
from app.measurement.domain import MeasurementReference
from app.measurement.domain import MeasurementUnit
from app.measurement.domain.registry import MeasurementRegistry


class DefaultMeasurementCatalog:

    @classmethod
    def build(
        cls,
    ) -> MeasurementRegistry:
        registry = MeasurementRegistry()

        for definition in cls.definitions():
            registry.register(
                definition
            )

        return registry

    @classmethod
    def definitions(
        cls,
    ) -> list[MeasurementDefinition]:
        standards = (
            MeasurementReference(
                title="ISO/IEC 25010 software quality model",
                source="ISO/IEC",
                identifier="25010",
            ),
            MeasurementReference(
                title="Guide to the Expression of Uncertainty in Measurement",
                source="JCGM",
                identifier="GUM",
            ),
        )

        return [
            MeasurementDefinition(
                id="code_churn",
                name="Code Churn",
                description=(
                    "Total added and deleted lines in the observed change."
                ),
                unit=MeasurementUnit.LOC,
                version="1.0",
                minimum=0.0,
                concept_id="change_impact",
                category="behavioral",
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                required_signals=(
                    "total_additions",
                    "total_deletions",
                ),
                normalizer="identity",
                aggregation_strategy="sum",
                references=standards,
                tags=("behavioral", "repository"),
            ),
            MeasurementDefinition(
                id="files_changed",
                name="Files Changed",
                description=(
                    "Number of artifacts touched by the observed change."
                ),
                unit=MeasurementUnit.COUNT,
                version="1.0",
                minimum=0.0,
                concept_id="change_impact",
                category="behavioral",
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                required_signals=("files",),
                normalizer="identity",
                aggregation_strategy="sum",
                references=standards,
                tags=("behavioral", "structural"),
            ),
            MeasurementDefinition(
                id="patch_complexity_delta",
                name="Patch Complexity Delta",
                description=(
                    "Deterministic approximation of control-flow "
                    "complexity introduced by changed patch lines."
                ),
                unit=MeasurementUnit.COMPLEXITY,
                version="1.0",
                concept_id="complexity",
                category="structural",
                required_signals=("patch",),
                normalizer="identity",
                aggregation_strategy="sum",
                references=standards,
                tags=("structural", "complexity"),
            ),
            MeasurementDefinition(
                id="change_distribution_entropy",
                name="Change Distribution Entropy",
                description=(
                    "Entropy of line changes across touched files."
                ),
                unit=MeasurementUnit.ENTROPY,
                version="1.0",
                minimum=0.0,
                concept_id="information_distribution",
                category="information_theory",
                expected_range=ExpectedRange(
                    minimum=0.0,
                ),
                required_signals=("file_changes",),
                normalizer="identity",
                aggregation_strategy="mean",
                references=standards,
                tags=("information", "behavioral"),
            ),
            MeasurementDefinition(
                id="change_surface_area",
                name="Change Surface Area",
                description=(
                    "Deterministic size-and-spread score for the "
                    "observed change."
                ),
                unit=MeasurementUnit.SCORE,
                version="1.0",
                minimum=0.0,
                maximum=100.0,
                concept_id="change_impact",
                category="impact",
                expected_range=ExpectedRange(
                    minimum=0.0,
                    maximum=100.0,
                ),
                required_signals=(
                    "total_changes",
                    "files_changed",
                ),
                normalizer="bounded_score_clamp",
                aggregation_strategy="weighted_mean",
                references=standards,
                tags=("impact", "behavioral"),
            ),
            MeasurementDefinition(
                id="review_attention_need",
                name="Review Attention Need",
                description=(
                    "Normalized review attention score derived from "
                    "churn, spread, deletions and patch availability."
                ),
                unit=MeasurementUnit.SCORE,
                version="1.0",
                minimum=0.0,
                maximum=100.0,
                concept_id="change_impact",
                category="review",
                expected_range=ExpectedRange(
                    minimum=0.0,
                    maximum=100.0,
                ),
                formula=(
                    "surface_area * 0.65 + deletion_ratio * 20 + "
                    "missing_patch_ratio * 15"
                ),
                dependencies=(
                    "change_surface_area",
                ),
                required_signals=(
                    "total_changes",
                    "files_changed",
                    "patch",
                ),
                normalizer="bounded_score_clamp",
                aggregation_strategy="weighted_mean",
                references=standards,
                tags=("impact", "review"),
            ),
        ]


