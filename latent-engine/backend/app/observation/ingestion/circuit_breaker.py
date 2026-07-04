import time
import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitOpenException(Exception):
    """Raised when the circuit is OPEN, preventing network calls."""
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 60.0):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time = 0.0

    def is_open(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return False
            
        if self.state == CircuitState.OPEN:
            # Check if it's time to test the circuit (HALF_OPEN)
            if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                logger.info("CircuitBreaker entering HALF_OPEN state (probing).")
                return False
            return True
            
        if self.state == CircuitState.HALF_OPEN:
            # While half-open, only allow one probe at a time, but for simplicity here we return False.
            # Real-world could use a lock to strictly allow ONE call.
            return False
            
        return False

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            logger.info("CircuitBreaker probe succeeded. Entering CLOSED state.")
            self.state = CircuitState.CLOSED
        self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            logger.warning("CircuitBreaker tripped to OPEN state.")
            self.state = CircuitState.OPEN

    def call(self, func, *args, **kwargs):
        """Execute a function protected by the circuit breaker."""
        if self.is_open():
            raise CircuitOpenException(f"Circuit is OPEN. Try again after {self.recovery_timeout_sec}s.")
            
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e
