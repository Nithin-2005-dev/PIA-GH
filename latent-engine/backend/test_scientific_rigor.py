import random
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta

from app.measurement.scientific.confidence_calibration import ECECalibrationEngine
from app.measurement.scientific.scientific_validation import MonteCarloValidationEngine

@dataclass
class MockPrediction:
    predicted_confidence: float
    actual_is_correct: bool

@dataclass
class MockEvent:
    id: str
    timestamp: datetime

def test_ece():
    print("--- Test 1: Expected Calibration Error (ECE) ---")
    engine = ECECalibrationEngine(num_bins=10)
    
    # Generate 100 mock predictions. Adapter always predicts 0.9.
    # But it's only correct 50% of the time.
    predictions = []
    for i in range(100):
        actual_is_correct = (i % 2 == 0) # exactly 50%
        predictions.append(MockPrediction(predicted_confidence=0.9, actual_is_correct=actual_is_correct))
        
    ece = engine.calculate_ece(predictions)
    print(f"Calculated ECE: {ece}")
    
    # Since confidence is always 0.9, and accuracy is always 0.5. The absolute error is 0.4.
    assert abs(ece - 0.4) < 0.01, f"Expected ECE around 0.4, got {ece}"
    print("Test 1 Passed: ECE perfectly isolates the adapter hallucination.\n")


def test_causal_jitter():
    print("--- Test 2: Monte Carlo Causal Jitter ---")
    engine = MonteCarloValidationEngine()
    
    base_time = datetime.now(UTC)
    events = [
        MockEvent("evt_1", base_time),
        MockEvent("evt_2", base_time + timedelta(seconds=10)),
        MockEvent("evt_3", base_time + timedelta(seconds=20))
    ]
    
    # We set random seed so we can predictably test the jitter without being purely flaky,
    # though for dropout to occur we might want to run a few times or force it.
    random.seed(42) 
    
    # Run multiple times to observe dropout and jitter
    dropouts = 0
    out_of_order = 0
    
    for _ in range(100):
        perturbed = engine._perturb_causal_graph(events)
        
        if len(perturbed) < len(events):
            dropouts += 1
            
        # Verify strict causal sorting despite jitter
        for i in range(len(perturbed) - 1):
            if perturbed[i].timestamp > perturbed[i+1].timestamp:
                out_of_order += 1
                
    print(f"Observed Dropouts across 100 runs: {dropouts}")
    print(f"Observed Out-of-Order causality: {out_of_order}")
    
    assert dropouts > 0, "Expected at least some events to be dropped by 1% simulation"
    assert out_of_order == 0, "Causality violated! Events were not sorted after jitter."
    print("Test 2 Passed: Causal Jitter successfully mutates history while preserving linear time.\n")

if __name__ == "__main__":
    test_ece()
    test_causal_jitter()
