import sys
import os
sys.path.append('.')
from app.cognitive.semantic_parser import SemanticQueryParser
from app.cognitive.provider import LLMProvider
from app.cognitive.goal_builder import GoalGraphBuilder
from app.cognitive.retriever import CapabilityRetriever
from app.cognitive.registry import CapabilityRegistry

class DummyProvider(LLMProvider):
    def generate(self, prompt, **kwargs):
        print("Fallback LLM invoked!")
        return '{"goals": ["UNKNOWN"], "confidence": 0.0}'
    def stream(self, prompt, **kwargs):
        pass

registry = CapabilityRegistry()
parser = SemanticQueryParser(DummyProvider())
builder = GoalGraphBuilder()
retriever = CapabilityRetriever(registry)

def test(query):
    print(f"\n--- Testing: {query} ---")
    sq = parser.parse(query)
    print("SemanticQuery Goals:", [g.name for g in sq.goals])
    
    graph = builder.build(sq)
    print("GoalGraph Nodes:", [n.goal.name for n in graph.nodes])
    
    # Fake knowledge
    class FakeKnowledge:
        def search_entities(self, *a, **k): return []
        adapter = None
    
    candidates = retriever.retrieve(graph, FakeKnowledge())
    print("Candidates:", [(c.card.name, c.score) for c in candidates])

test("how is this org health?")
test("what is the health of this project?")
test("generate knowledge graph")
test("who is the best dev in this org?")
