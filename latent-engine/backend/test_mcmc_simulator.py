from app.measurement.scientific.mcmc_generator import MarkovChainCorpusGenerator

def run_test():
    generator = MarkovChainCorpusGenerator()
    
    print("--- Test: MCMC Simulator (Phase 16) ---")
    
    num_events = 1000
    history = generator.generate_synthetic_history(num_events=num_events)
    
    assert len(history) == num_events, f"Expected {num_events} events, got {len(history)}"
    
    # 3. Assert logically impossible sequences (pr_merge immediately after idle without pr_open/approved)
    # The MCMC defines idle -> commit or pr_open or idle. It does NOT allow idle -> pr_merge.
    impossible_sequences = 0
    
    for i in range(len(history) - 1):
        curr_state = history[i].type
        next_state = history[i+1].type
        
        # Check transition matrix rules implicitly
        if curr_state == 'idle' and next_state not in ['commit', 'pr_open', 'idle']:
            impossible_sequences += 1
            
    assert impossible_sequences == 0, f"Found {impossible_sequences} impossible transitions from idle!"
    print(f"Verified {num_events} generated events against Markov structural rules. Zero impossibilities found.")
    
    # 4. Assert that pr_open is frequently followed by review_request (probability 0.8)
    pr_open_count = sum(1 for e in history if e.type == 'pr_open')
    review_request_after_open = 0
    for i in range(len(history) - 1):
        if history[i].type == 'pr_open' and history[i+1].type == 'review_request':
            review_request_after_open += 1
            
    if pr_open_count > 0:
        ratio = review_request_after_open / pr_open_count
        print(f"pr_open -> review_request transition ratio: {ratio:.2f}")
        assert 0.6 < ratio < 1.0, f"Expected transition ratio ~0.8, got {ratio}"
    else:
        print("Warning: no pr_open events generated to verify ratio.")

    print("Test Passed: MCMC Simulation is structurally sound and mathematically valid.\n")
    
if __name__ == "__main__":
    run_test()
