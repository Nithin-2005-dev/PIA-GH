from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementKnowledgeEntry:
    concept_id: str
    scientific_references: tuple[str, ...] = ()
    standards: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = ()
    recommended_interpretation: str | None = None
    anti_patterns: tuple[str, ...] = ()
    normalization_notes: tuple[str, ...] = ()


class MeasurementKnowledgeBase:

    def __init__(
        self,
    ):
        self._entries = {}

    def register(
        self,
        entry: MeasurementKnowledgeEntry,
    ):
        self._entries[
            entry.concept_id
        ] = entry

    def get(
        self,
        concept_id: str,
    ) -> MeasurementKnowledgeEntry | None:
        return self._entries.get(
            concept_id
        )
