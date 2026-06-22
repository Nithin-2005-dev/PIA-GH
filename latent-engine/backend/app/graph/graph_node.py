from dataclasses import dataclass


@dataclass(frozen=True)
class GraphNode:
    """
    Generic graph node.
    """

    id: str

    type: str