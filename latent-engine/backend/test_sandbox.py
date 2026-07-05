import traceback
import time
from app.measurement.plugins_runtime.plugins import PluginEngine

def hang():
    time.sleep(5)

def run_test():
    engine = PluginEngine()
    
    print("--- Test 1: Math Execution ---")
    script1 = "code_churn * math.log(complexity)"
    context1 = {"code_churn": 10.0, "complexity": 2.71828} # math.log(e) ~ 1.0
    result1 = engine.execute_untrusted_plugin(script1, context1)
    print(f"Result: {result1}")
    assert abs(result1 - 10.0) < 0.1
    print("Test 1 Passed: Valid DSL executes correctly.\n")
    
    print("--- Test 2: Context Escape Prevention ---")
    script2 = "__import__('os').system('echo hacked')"
    try:
        engine.execute_untrusted_plugin(script2, {})
        assert False, "Should have thrown a Security/Name Error"
    except Exception as e:
        print(f"Caught Expected Exception: {type(e).__name__}: {e}")
        assert "name '__import__' is not defined" in str(e) or "__import__" in str(e)
    print("Test 2 Passed: Context escape prevented.\n")
    
    print("--- Test 3: The Halting Problem (Timeout) ---")
    script3 = "hang()"
    try:
        engine.execute_untrusted_plugin(script3, {"hang": hang})
        assert False, "Should have thrown a TimeoutError"
    except TimeoutError as e:
        print(f"Caught Expected Exception: TimeoutError")
    print("Test 3 Passed: Infinite loop terminated safely.\n")

if __name__ == "__main__":
    run_test()
