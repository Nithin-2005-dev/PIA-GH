from app.measurement.domain import MeasurementConcept
from app.measurement.domain import MeasurementReference


class MeasurementOntology:

    def __init__(
        self,
        concepts: list[MeasurementConcept],
    ):
        self._concepts = {
            concept.id: concept
            for concept in concepts
        }

    @classmethod
    def default(
        cls,
    ):
        references = (
            MeasurementReference(
                title="ISO/IEC 25010 software quality model",
                source="ISO/IEC",
                identifier="25010",
            ),
            MeasurementReference(
                title="ISO/IEC 15939 measurement process",
                source="ISO/IEC",
                identifier="15939",
            ),
            MeasurementReference(
                title="Guide to the Expression of Uncertainty in Measurement",
                source="JCGM",
                identifier="GUM",
            ),
        )

        return cls(
            concepts=[
                MeasurementConcept(
                    id="maintainability",
                    display_name="Maintainability",
                    scientific_meaning=(
                        "Ability of a software artifact to be modified "
                        "effectively and safely over time."
                    ),
                    category="software_quality",
                    dimensions=(
                        "complexity",
                        "readability",
                        "coupling",
                        "documentation",
                        "ownership",
                        "testability",
                    ),
                    references=references,
                ),
                MeasurementConcept(
                    id="complexity",
                    display_name="Complexity",
                    scientific_meaning=(
                        "Structural and behavioral effort required to "
                        "understand or change an artifact."
                    ),
                    category="structural",
                    parent_id="maintainability",
                    references=references,
                ),
                MeasurementConcept(
                    id="change_impact",
                    display_name="Change Impact",
                    scientific_meaning=(
                        "Expected review and coordination load introduced "
                        "by an observed change."
                    ),
                    category="delivery",
                    parent_id="maintainability",
                    references=references,
                ),
                MeasurementConcept(
                    id="information_distribution",
                    display_name="Information Distribution",
                    scientific_meaning=(
                        "Dispersion of observed engineering activity across "
                        "artifacts, people or time."
                    ),
                    category="information_theory",
                    references=references,
                ),
            ],
        )

    def get(
        self,
        concept_id: str,
    ) -> MeasurementConcept:
        return self._concepts[
            concept_id
        ]

    def children_of(
        self,
        concept_id: str,
    ) -> list[MeasurementConcept]:
        return [
            concept
            for concept in self._concepts.values()
            if concept.parent_id == concept_id
        ]

    def all(
        self,
    ) -> list[MeasurementConcept]:
        return list(
            self._concepts.values()
        )


