from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

from app.platform.common import utc_now

logger = logging.getLogger(__name__)

class EventPriority(IntEnum):
    LOW = 10
    NORMAL = 50
    HIGH = 100

@dataclass(frozen=True)
class PlatformEvent:
    type: str
    payload: Any
    version: str = "1.0"
    priority: EventPriority = EventPriority.NORMAL
    event_id: str = ""
    correlation_id: str | None = None
    trace_id: str | None = None
    occurred_at: object | None = None

    def normalized(self) -> "PlatformEvent":
        return PlatformEvent(
            type=self.type,
            payload=self.payload,
            version=self.version,
            priority=self.priority,
            event_id=self.event_id or str(uuid4()),
            correlation_id=self.correlation_id,
            trace_id=self.trace_id,
            occurred_at=self.occurred_at or utc_now(),
        )
        
    def __lt__(self, other):
        # PriorityQueue pops lowest first, so we invert the priority value
        # and then use timestamp or event_id as secondary sort
        if not isinstance(other, PlatformEvent):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority > other.priority
        # Fallback to FIFO based on event_id or timestamp
        return str(self.occurred_at) < str(other.occurred_at)

@dataclass(frozen=True)
class DeadLetter:
    event: PlatformEvent
    error: str

class EventBus:
    """
    Asynchronous event bus enabling concurrent execution of telemetry tasks.
    Supports both synchronous dispatch (for tests/legacy) and concurrent
    asynchronous background workers (when start() is called).
    """
    def __init__(self, num_workers: int = 4, queue_size: int = 10000):
        self._subscribers: dict[str, list[Callable[[PlatformEvent], None]]] = defaultdict(list)
        self._async_subscribers: dict[str, list[Callable[[PlatformEvent], Any]]] = defaultdict(list)
        self._history: list[PlatformEvent] = []
        self._dead_letters: list[DeadLetter] = []
        
        self.num_workers = num_workers
        self.queue_size = queue_size
        self._queue: Optional[asyncio.PriorityQueue] = None
        self._workers: List[asyncio.Task] = []
        self._stop_event: Optional[asyncio.Event] = None
        self._started = False

    def subscribe(self, event_type: str, handler: Callable[[PlatformEvent], None]) -> None:
        """Subscribe a synchronous handler. Will be run in a thread by workers."""
        self._subscribers[event_type].append(handler)
        
    def subscribe_async(self, event_type: str, handler: Callable[[PlatformEvent], Any]) -> None:
        """Subscribe an asynchronous handler."""
        self._async_subscribers[event_type].append(handler)

    async def start(self) -> None:
        """Start the background worker tasks."""
        if self._started:
            return
        
        # We use a PriorityQueue to respect EventPriority
        self._queue = asyncio.PriorityQueue(maxsize=self.queue_size)
        self._stop_event = asyncio.Event()
        self._started = True
        
        for i in range(self.num_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self._workers.append(task)
            
        logger.info(f"EventBus started with {self.num_workers} concurrent workers.")

    async def stop(self, timeout: float = 5.0) -> None:
        """Gracefully stop the workers, waiting for the queue to drain."""
        if not self._started:
            return
            
        logger.info("EventBus stopping. Waiting for queue to drain...")
        self._stop_event.set()
        
        # Wait for queue to empty
        if self._queue:
            try:
                await asyncio.wait_for(self._queue.join(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning("EventBus stop timeout. Some events may not be processed.")
                
        # Cancel workers
        for worker in self._workers:
            worker.cancel()
            
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        self._started = False
        logger.info("EventBus stopped.")

    async def _worker_loop(self, worker_id: int) -> None:
        """Background worker loop processing events concurrently."""
        while True:
            try:
                # Wait for an event, or cancellation
                event = await self._queue.get()
                try:
                    await self._dispatch_async(event)
                except Exception as exc:
                    self._dead_letters.append(DeadLetter(event=event, error=str(exc)))
                    logger.error(f"Worker {worker_id} failed to process event {event.type}: {exc}")
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker {worker_id}: {e}")

    async def _dispatch_async(self, event: PlatformEvent) -> None:
        """Dispatch event to both sync and async handlers concurrently."""
        handlers = [
            *self._subscribers.get("*", []),
            *self._subscribers.get(event.type, []),
        ]
        
        async_handlers = [
            *self._async_subscribers.get("*", []),
            *self._async_subscribers.get(event.type, []),
        ]
        
        tasks = []
        
        # Dispatch to async handlers
        for handler in async_handlers:
            tasks.append(asyncio.create_task(handler(event)))
            
        # Dispatch to sync handlers by offloading to a thread to prevent blocking the event loop
        for handler in handlers:
            tasks.append(asyncio.to_thread(handler, event))
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    raise result

    def _dispatch_sync(self, event: PlatformEvent) -> None:
        """Fallback synchronous dispatch for tests or legacy pipelines."""
        handlers = [
            *self._subscribers.get("*", []),
            *self._subscribers.get(event.type, []),
        ]
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                self._dead_letters.append(DeadLetter(event=event, error=str(exc)))
                logger.error(f"Sync dispatch failed for {event.type}: {exc}")

    def publish(self, event: PlatformEvent) -> PlatformEvent:
        """
        Publishes an event. If workers are started, it is enqueued for concurrent execution.
        Otherwise, it is dispatched synchronously. Returns immediately.
        """
        normalized = event.normalized()
        self._history.append(normalized)
        
        if self._started and self._queue is not None:
            try:
                self._queue.put_nowait(normalized)
            except asyncio.QueueFull:
                self._dead_letters.append(DeadLetter(event=normalized, error="Queue Full / Backpressure applied"))
                logger.warning(f"EventBus queue full. Dropped event {normalized.type}")
        else:
            self._dispatch_sync(normalized)
            
        return normalized

    def publish_many(self, events: list[PlatformEvent]) -> tuple[PlatformEvent, ...]:
        ordered = sorted(events, key=lambda event: int(event.priority), reverse=True)
        return tuple(self.publish(event) for event in ordered)

    def replay(self, event_type: str | None = None) -> tuple[PlatformEvent, ...]:
        return tuple(event for event in self._history if event_type is None or event.type == event_type)

    def dead_letters(self) -> tuple[DeadLetter, ...]:
        return tuple(self._dead_letters)


_event_bus_instance: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(num_workers=4, queue_size=10000)
    return _event_bus_instance

