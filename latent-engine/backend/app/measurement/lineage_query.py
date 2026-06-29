from .lineage import MeasurementLineageGraph


class MeasurementLineageQueryEngine:

    def show_path(
        self,
        graph: MeasurementLineageGraph,
        source_id: str,
        target_id: str,
    ) -> list[str]:
        adjacency = {}

        for edge in graph.edges:
            adjacency.setdefault(
                edge.source_id,
                [],
            ).append(
                edge.target_id
            )

        frontier = [
            (
                source_id,
                [
                    source_id
                ],
            )
        ]
        visited = set()

        while frontier:
            current, path = frontier.pop(0)

            if current == target_id:
                return path

            if current in visited:
                continue

            visited.add(
                current
            )

            for target in adjacency.get(
                current,
                [],
            ):
                frontier.append(
                    (
                        target,
                        [
                            *path,
                            target,
                        ],
                    )
                )

        return []

    def show_dependents(
        self,
        graph: MeasurementLineageGraph,
        measurement_id: str,
    ) -> list[str]:
        return [
            edge.target_id
            for edge in graph.edges
            if edge.source_id == measurement_id
            and edge.relationship in {
                "depends_on",
                "computed_as",
            }
        ]
