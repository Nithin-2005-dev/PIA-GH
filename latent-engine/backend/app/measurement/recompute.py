from collections import defaultdict


class MeasurementDependencyGraph:

    def __init__(
        self,
    ):
        self._dependents = defaultdict(set)

    def register(
        self,
        measurement_id: str,
        dependencies: tuple[str, ...],
    ):
        for dependency_id in dependencies:
            self._dependents[dependency_id].add(
                measurement_id
            )

    def affected_by(
        self,
        changed_measurement_id: str,
    ) -> set[str]:
        affected = set()
        frontier = [
            changed_measurement_id
        ]

        while frontier:
            current = frontier.pop()

            for dependent in self._dependents.get(
                current,
                set(),
            ):
                if dependent in affected:
                    continue

                affected.add(
                    dependent
                )
                frontier.append(
                    dependent
                )

        return affected
