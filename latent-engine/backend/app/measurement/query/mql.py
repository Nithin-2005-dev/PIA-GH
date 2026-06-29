from dataclasses import dataclass

from app.measurement.domain import Measurement


@dataclass(frozen=True)
class MqlQuery:
    definition_id: str | None = None
    minimum_confidence: float | None = None
    repository: str | None = None
    order_by: str | None = None
    descending: bool = True


class MqlParser:

    def parse(
        self,
        text: str,
    ) -> MqlQuery:
        tokens = text.replace(
            "\n",
            " ",
        ).split()

        definition_id = None
        minimum_confidence = None
        repository = None
        order_by = None

        if "SELECT" in tokens:
            index = tokens.index(
                "SELECT"
            )
            definition_id = tokens[
                index + 1
            ]

        if "confidence" in tokens and ">" in tokens:
            index = tokens.index(
                "confidence"
            )
            minimum_confidence = float(
                tokens[
                    index + 2
                ]
            )

        if "repository" in tokens and "=" in tokens:
            index = tokens.index(
                "repository"
            )
            repository = tokens[
                index + 2
            ].strip(
                "\"'"
            )

        if "ORDER" in tokens and "BY" in tokens:
            index = tokens.index(
                "BY"
            )
            order_by = tokens[
                index + 1
            ]

        return MqlQuery(
            definition_id=definition_id,
            minimum_confidence=minimum_confidence,
            repository=repository,
            order_by=order_by,
        )


class MqlEngine:

    def query(
        self,
        measurements: list[Measurement],
        query: MqlQuery,
    ) -> list[Measurement]:
        results = []

        for measurement in measurements:
            if (
                query.definition_id is not None
                and measurement.definition.id
                != query.definition_id
            ):
                continue

            if (
                query.minimum_confidence is not None
                and measurement.confidence
                <= query.minimum_confidence
            ):
                continue

            if query.repository is not None:
                repository = measurement.metadata.get(
                    "repository"
                )

                if repository != query.repository:
                    continue

            results.append(
                measurement
            )

        if query.order_by is not None:
            results.sort(
                key=lambda measurement: getattr(
                    measurement,
                    query.order_by,
                ),
                reverse=query.descending,
            )

        return results


