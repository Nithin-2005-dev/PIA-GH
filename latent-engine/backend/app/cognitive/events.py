import time
from enum import Enum
from typing import Callable, Dict, List, Any
from .models import RuntimeEvent

class EventType(str, Enum):
    # Lifecycle
    PlannerStarted = "PlannerStarted"
    PlannerFinished = "PlannerFinished"
    PlannerReplanned = "PlannerReplanned"
    
    # Goals
    GoalCreated = "GoalCreated"
    GoalCompleted = "GoalCompleted"
    
    # Capabilities & Tools
    CapabilitySelected = "CapabilitySelected"
    CapabilityRejected = "CapabilityRejected"
    ToolStarted = "ToolStarted"
    ToolFinished = "ToolFinished"
    ToolCached = "ToolCached"
    
    # Providers
    ProviderStarted = "ProviderStarted"
    ProviderFinished = "ProviderFinished"
    ProviderFailover = "ProviderFailover"
    ProviderRetry = "ProviderRetry"
    
    # Memory & Evidence
    EvidenceRetrieved = "EvidenceRetrieved"
    EvidenceRejected = "EvidenceRejected"
    MemoryUpdated = "MemoryUpdated"
    
    # Verification & Reflection
    VerificationStarted = "VerificationStarted"
    AnswerVerified = "AnswerVerified"
    ReflectionStarted = "ReflectionStarted"
    ReflectionFinished = "ReflectionFinished"
    
    # Policy
    PolicyDecision = "PolicyDecision"
    
    # Synthesis
    AnswerStarted = "AnswerStarted"
    AnswerStreaming = "AnswerStreaming"
    AnswerFinished = "AnswerFinished"

class EventBus:
    """
    Central event bus for the Cognitive Runtime.
    Allows decoupling of UI, telemetry, and benchmarks from the execution engine.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[RuntimeEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[RuntimeEvent], None]) -> None:
        """Subscribe to a specific event type, or '*' for all events."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[RuntimeEvent], None]) -> None:
        """Unsubscribe a callback from an event type."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, stage: str, **data: Any) -> None:
        """Publish an event to all subscribers."""
        event = RuntimeEvent(
            event_type=event_type,
            stage=stage,
            timestamp=time.perf_counter_ns() / 1e6, # milliseconds timestamp
            data=data
        )
        
        # Notify specific subscribers
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(event)
            except Exception:
                pass # Event handlers should not crash the runtime
                
        # Notify wildcard subscribers
        for callback in self._subscribers.get("*", []):
            try:
                callback(event)
            except Exception:
                pass

# Global instance for the runtime (or can be injected per session)
_global_bus = EventBus()

def get_event_bus() -> EventBus:
    return _global_bus
