from abc import ABC, abstractmethod

from app.domain.event import Event

from .event_query import EventQuery


class EventSourcePort(ABC):
    """
    Contract for external event sources.

    Implementations translate external systems into
    normalized domain Events.
    """

    @abstractmethod
    def collect(
        self,
        query: EventQuery,
    ) -> list[Event]:
        """
        Collect events satisfying the given query.

        Returns:
            A list of normalized immutable domain Events.
        """
        raise NotImplementedError