import asyncio
import pytest
from app.platform.event_bus import EventBus, PlatformEvent, EventPriority

pytestmark = pytest.mark.asyncio

async def test_api_start_returns_without_waiting():
    """
    Simulates the API returning immediately by checking that publish() 
    is non-blocking and the work happens in the background.
    """
    bus = EventBus(num_workers=1)
    await bus.start()
    
    processed = asyncio.Event()
    
    async def handler(event):
        await asyncio.sleep(0.1) # Simulate ingestion
        processed.set()
        
    bus.subscribe_async("sync.requested", handler)
    
    # Should return instantly
    bus.publish(PlatformEvent(type="sync.requested", payload={}))
    
    # Assert background work hasn't finished yet
    assert not processed.is_set()
    
    # Wait for background work
    await processed.wait()
    await bus.stop()

async def test_concurrent_processing():
    """Test that multiple events can be processed concurrently."""
    bus = EventBus(num_workers=3)
    await bus.start()
    
    active_workers = 0
    max_active = 0
    lock = asyncio.Lock()
    events_processed = 0
    
    async def slow_handler(event):
        nonlocal active_workers, max_active, events_processed
        async with lock:
            active_workers += 1
            if active_workers > max_active:
                max_active = active_workers
        
        await asyncio.sleep(0.1)
        
        async with lock:
            active_workers -= 1
            events_processed += 1

    bus.subscribe_async("test.event", slow_handler)
    
    # Publish 5 events
    for _ in range(5):
        bus.publish(PlatformEvent(type="test.event", payload={}))
        
    await asyncio.sleep(0.3)
    await bus.stop()
    
    assert max_active == 3  # We have 3 workers, so max concurrency is 3
    assert events_processed == 5

async def test_event_ordering():
    """Test that event ordering behavior is deterministic where required (PriorityQueue)."""
    bus = EventBus(num_workers=1) # 1 worker to ensure strict sequence
    await bus.start()
    
    processed_order = []
    
    async def handler(event):
        processed_order.append(event.payload['id'])
        
    bus.subscribe_async("priority.event", handler)
    
    # Pause worker by sending a slow event first
    release_event = asyncio.Event()
    
    async def blocker(event):
        if event.payload.get('block'):
            await release_event.wait()
            
    bus.subscribe_async("priority.event", blocker)
    
    bus.publish(PlatformEvent(type="priority.event", priority=EventPriority.NORMAL, payload={'id': 0, 'block': True}))
    
    # These will be queued
    bus.publish(PlatformEvent(type="priority.event", priority=EventPriority.LOW, payload={'id': 3}))
    bus.publish(PlatformEvent(type="priority.event", priority=EventPriority.HIGH, payload={'id': 1}))
    bus.publish(PlatformEvent(type="priority.event", priority=EventPriority.NORMAL, payload={'id': 2}))
    
    release_event.set()
    await asyncio.sleep(0.1)
    await bus.stop()
    
    # High priority (1) gets popped first, then NORMAL (0, 2), then LOW (3)
    assert processed_order == [1, 0, 2, 3]

async def test_consumer_failure_isolation():
    """Consumer failure does not kill unrelated consumers/workers."""
    bus = EventBus(num_workers=1)
    await bus.start()
    
    processed = []
    
    async def failing_handler(event):
        if event.payload['fail']:
            raise ValueError("Intentional Failure")
        processed.append(event.payload['id'])
        
    bus.subscribe_async("fail.event", failing_handler)
    
    bus.publish(PlatformEvent(type="fail.event", payload={'id': 1, 'fail': True}))
    bus.publish(PlatformEvent(type="fail.event", payload={'id': 2, 'fail': False}))
    
    await asyncio.sleep(0.1)
    await bus.stop()
    
    assert processed == [2] # Worker survived and processed the second event
    assert len(bus.dead_letters()) == 1
    assert "Intentional Failure" in bus.dead_letters()[0].error

async def test_backpressure_behavior():
    """Backpressure behavior works as designed."""
    bus = EventBus(num_workers=1, queue_size=2)
    # Note: NOT calling start() yet, so events will just queue up
    bus._queue = asyncio.PriorityQueue(maxsize=bus.queue_size)
    bus._started = True
    
    bus.publish(PlatformEvent(type="test", payload={}))
    bus.publish(PlatformEvent(type="test", payload={}))
    bus.publish(PlatformEvent(type="test", payload={})) # Should trigger backpressure
    
    assert len(bus.dead_letters()) == 1
    assert "Queue Full" in bus.dead_letters()[0].error
    
    bus._started = False

async def test_graceful_shutdown():
    """Shutdown/cancellation works correctly."""
    bus = EventBus(num_workers=1)
    await bus.start()
    
    processed = []
    async def slow_handler(event):
        await asyncio.sleep(0.1)
        processed.append(event.payload['id'])
        
    bus.subscribe_async("shutdown.event", slow_handler)
    
    bus.publish(PlatformEvent(type="shutdown.event", payload={'id': 1}))
    bus.publish(PlatformEvent(type="shutdown.event", payload={'id': 2}))
    
    # Call stop immediately. It should wait for queue to drain (timeout=5.0)
    await bus.stop()
    
    assert processed == [1, 2] # All queued events were processed before shutdown
