from dataclasses import dataclass

from app.evidence.domain import Evidence
from app.evidence.domain import EvidencePriority
from app.evidence.domain import EvidenceSeverity


@dataclass(frozen=True)
class EqlQuery:
    find: str
    filters: tuple[tuple[str, str, str], ...] = ()
    order_by: str | None = None
    descending: bool = True


class EqlParser:

    def parse(
        self,
        text: str,
    ) -> EqlQuery:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]
        if not lines or not lines[0].upper().startswith("FIND "):
            raise ValueError(
                "EQL query must start with FIND"
            )

        find = lines[0].split(
            maxsplit=1
        )[1]
        filters = []
        order_by = None
        descending = True

        for line in lines[1:]:
            upper = line.upper()
            if upper == "WHERE" or upper == "AND":
                continue
            if upper.startswith("ORDER BY "):
                parts = line.split()
                order_by = parts[2]
                descending = (
                    len(
                        parts
                    )
                    < 4
                    or parts[3].upper() == "DESC"
                )
                continue

            cleaned = line
            if cleaned.upper().startswith("AND "):
                cleaned = cleaned[4:]
            for operator in (">=", "<=", ">", "<", "==", "="):
                if operator in cleaned:
                    field, value = cleaned.split(
                        operator,
                        maxsplit=1,
                    )
                    filters.append(
                        (
                            field.strip(),
                            operator,
                            value.strip(),
                        )
                    )
                    break

        return EqlQuery(
            find=find,
            filters=tuple(
                filters
            ),
            order_by=order_by,
            descending=descending,
        )


class EqlEngine:

    def query(
        self,
        evidence: tuple[Evidence, ...],
        query: EqlQuery,
    ) -> tuple[Evidence, ...]:
        results = tuple(
            item
            for item in evidence
            if self._matches_find(
                item,
                query.find,
            )
            and all(
                self._matches_filter(
                    item,
                    field,
                    operator,
                    expected,
                )
                for field, operator, expected in query.filters
            )
        )

        if query.order_by:
            results = tuple(
                sorted(
                    results,
                    key=lambda item: self._field_value(
                        item,
                        query.order_by or "",
                    ),
                    reverse=query.descending,
                )
            )

        return results

    def _matches_find(
        self,
        evidence: Evidence,
        find: str,
    ) -> bool:
        if find.lower() in {
            "evidence",
            "all",
        }:
            return True
        return find.lower() in {
            evidence.name.replace(
                " ",
                "",
            ).lower(),
            evidence.category.lower(),
            evidence.evidence_id.lower(),
        } or find.lower() in evidence.name.lower()

    def _matches_filter(
        self,
        evidence: Evidence,
        field: str,
        operator: str,
        expected: str,
    ) -> bool:
        actual = self._field_value(
            evidence,
            field,
        )
        expected_value = self._parse_value(
            field,
            expected,
        )

        if operator in {
            "=",
            "==",
        }:
            return actual == expected_value
        if operator == ">":
            return actual > expected_value
        if operator == ">=":
            return actual >= expected_value
        if operator == "<":
            return actual < expected_value
        if operator == "<=":
            return actual <= expected_value
        return False

    def _field_value(
        self,
        evidence: Evidence,
        field: str,
    ):
        normalized = field.lower()
        if normalized == "confidence":
            return evidence.confidence
        if normalized == "severity":
            return evidence.severity.rank()
        if normalized == "priority":
            return evidence.priority.rank()
        if normalized == "quality":
            return evidence.quality
        if normalized == "strength":
            return evidence.strength
        if normalized == "category":
            return evidence.category
        return evidence.metadata.get(
            field,
            ""
        )

    def _parse_value(
        self,
        field: str,
        value: str,
    ):
        normalized = field.lower()
        cleaned = value.strip().strip('"').strip("'")
        if normalized == "severity":
            return EvidenceSeverity[
                cleaned.upper()
            ].rank()
        if normalized == "priority":
            return EvidencePriority[
                cleaned.upper()
            ].rank()
        try:
            return float(
                cleaned
            )
        except ValueError:
            return cleaned

