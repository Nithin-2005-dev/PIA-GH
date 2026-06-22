from app.graph.organizational_graph import (
    OrganizationalGraph,
)


class GraphService:

    def __init__(
        self,
        graph: OrganizationalGraph,
    ):
        self._graph = graph

    def outgoing(
        self,
        node_id: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if edge.source_id == node_id
        ]

    def incoming(
        self,
        node_id: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if edge.target_id == node_id
        ]

    def neighbors(
        self,
        node_id: str,
    ):

        neighbor_ids = set()

        for edge in self._graph.edges:

            if edge.source_id == node_id:

                neighbor_ids.add(
                    edge.target_id
                )

            elif edge.target_id == node_id:

                neighbor_ids.add(
                    edge.source_id
                )

        return [
            node
            for node in self._graph.nodes
            if node.id in neighbor_ids
        ]

    def find_by_relationship(
        self,
        relationship: str,
    ):

        return [
            edge
            for edge in self._graph.edges
            if (
                edge.relationship
                == relationship
            )
        ]