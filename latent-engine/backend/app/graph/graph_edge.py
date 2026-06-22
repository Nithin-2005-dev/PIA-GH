from dataclasses import dataclass


@dataclass(frozen=True)
class GraphEdge:
    """
    Directed relationship
    between two nodes.
    """

    source_id: str

    target_id: str

    relationship: str

    weight: float = 1.0