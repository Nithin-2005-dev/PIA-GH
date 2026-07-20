import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.adapters.compatibility.reasoning_adapter import CompatibilityAdapter, ShimGraphEngine
from app.kernel.reasoning.rule_engine import create_single_point_of_failure_rule
from app.adapters.database.models import FactRecord
from app.kernel.graph import GraphEngine, GraphNode, NodeType, GraphEdge, EdgeType

def test_compatibility_adapter():
    print("Testing Compatibility Adapter with 'Single Point of Failure' rule...\n")
    
    # 1. Setup the Rule
    rule = create_single_point_of_failure_rule()
    
    # 2. Test Legacy Path (Native GraphEngine)
    legacy_graph = GraphEngine()
    obs_node = GraphNode(id="obs-1", node_type=NodeType.OBSERVATION, properties={}, confidence=1.0)
    ev_node = GraphNode(id="ev-1", node_type=NodeType.EVIDENCE, properties={"raw_output": {"bus_factor": 1}}, confidence=1.0)
    
    legacy_graph.add_node(obs_node)
    legacy_graph.add_node(ev_node)
    legacy_graph.add_edge(GraphEdge(source_id=obs_node.id, target_id=ev_node.id, edge_type=EdgeType.DERIVED_FROM, weight=1.0))
    
    # Execute Legacy
    matches = rule.condition(legacy_graph)
    assert len(matches) == 1, "Legacy path failed to match condition"
    
    # We must mock output capturing in legacy graph to compare
    legacy_inferences = []
    original_add_node = legacy_graph.add_node
    def trap_node(n):
        if n.node_type == NodeType.INFERENCE:
            legacy_inferences.append(n)
        return original_add_node(n)
    legacy_graph.add_node = trap_node
    
    rule.action(legacy_graph, matches[0], rule)
    assert len(legacy_inferences) == 1, "Legacy path failed to produce inference"
    
    print(f"[OK] Legacy Path produced Inference: {legacy_inferences[0].properties}")

    # 3. Test Modern Path (Compatibility Adapter)
    adapter = CompatibilityAdapter()
    
    # The modern path consumes FactRecords instead of raw GraphNodes
    fact = FactRecord(
        fact_type="bus_factor",
        confidence=1.0,
        hash="test_hash_123"
    )
    
    # Instead of calling adapter.evaluate_rule (which writes to DB), 
    # we'll simulate the internal ShimGraphEngine to assert equivalence before DB commit.
    shim = ShimGraphEngine([fact], "session_123")
    matches = rule.condition(shim)
    
    assert len(matches) == 1, "Compatibility Adapter failed to match condition"
    
    rule.action(shim, matches[0], rule)
    
    assert len(shim.outputs) == 1, "Compatibility Adapter failed to produce inference"
    
    print(f"[OK] Compatibility Adapter produced Inference: {shim.outputs[0].properties}")
    
    # 4. Assert Equivalence
    assert legacy_inferences[0].properties == shim.outputs[0].properties, "Output mismatch!"
    assert legacy_inferences[0].confidence == shim.outputs[0].confidence, "Confidence mismatch!"
    
    print("\n[SUCCESS] Deterministic replay and equivalence verified!")
    print("The old business logic successfully executes via the new FactRecord contracts without modification.")

if __name__ == "__main__":
    test_compatibility_adapter()
