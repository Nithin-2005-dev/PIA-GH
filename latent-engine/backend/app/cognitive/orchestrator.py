import time
import dataclasses
import json
import uuid

from .models import ExecutionState, ExecutionStatus, AnswerConfidence, CognitiveAnswer, VerificationResult, StageResult, ExecutiveResponse, Intent
from .planner import PlanningEngine
from .executor import CapabilityPlanner, Executor
from .reflection import ReflectionEngine
from .policy import PolicyEngine
from .events import get_event_bus
from .answer_builder import AnswerBuilder
from .synthesizer import AdaptiveSynthesizer
from .decomposer import GoalDecomposer
from .tool_search import ToolSearchEngine, KeywordSearchEngine
from .invariants import InvariantChecker
from .models import PreconditionFailure, CapabilityResult, RepositoryMemory
from .validation import CapabilityValidator
from .semantic_parser import SemanticQueryParser
from .retriever import CapabilityRetriever
from .entity_resolver import EntityResolver
from .repository_knowledge import RepositoryKnowledge
from .adapter import PlatformResultAdapter
from .goal_builder import GoalGraphBuilder

class AgentOrchestrator:
    """
    The main execution loop for the Agentic Runtime (M58).
    Pipeline: SemanticParser -> CapabilityRetriever -> Planner -> Executor -> AnswerBuilder -> Synthesizer
    """
    def __init__(
        self,
        planner: PlanningEngine,
        executor: Executor,
        capability_planner: CapabilityPlanner,
        reflection_engine: ReflectionEngine,
        policy_engine: PolicyEngine,
        answer_builder: AnswerBuilder,
        synthesizer: AdaptiveSynthesizer,
        semantic_parser: SemanticQueryParser,
        retriever: CapabilityRetriever,
        entity_resolver: EntityResolver,
        registry
    ):
        self.semantic_parser = semantic_parser
        self.retriever = retriever
        self.entity_resolver = entity_resolver
        self.planner = planner
        self.executor = executor
        self.capability_planner = capability_planner
        self.reflection_engine = reflection_engine
        self.policy_engine = policy_engine
        self.answer_builder = answer_builder
        self.synthesizer = synthesizer
        self.registry = registry
        self.event_bus = get_event_bus()
        self.invariant_checker = InvariantChecker()
        self.goal_graph_builder = GoalGraphBuilder()

    def run(self, state: ExecutionState) -> ExecutionState:
        iteration = 0
        stage_results = list(state.stage_results)
        
        def add_stage(name, status, exp_in, exp_out, act_out, dur, diag, reason=None):
            sr = StageResult(
                stage_id=f"{state.query_id}_{len(stage_results)}",
                stage_name=name,
                status=status,
                expected_input=exp_in,
                expected_output=exp_out,
                actual_output=act_out,
                duration_ms=dur,
                diagnostics=diag,
                reason=reason
            )
            stage_results.append(sr)
            return sr
            
        def abort_with_error(stage_name, reason, diagnostics, status=ExecutionStatus.RUNTIME_FAILURE):
            self._print_health_matrix(stage_results)
            exec_resp = ExecutiveResponse(
                executive_summary="Repository query could not be executed.",
                technical_summary=f"Diagnostic Error at [{stage_name}]:\nReason: {reason}\nDiagnostics:\n{json.dumps(diagnostics, indent=2, default=str)}",
                actionable_recommendations=["Improve semantic routing or capability retrieval."],
                supporting_evidence=[], confidence=0.0, risks=[], alternative_strategies=[]
            )
            return dataclasses.replace(state, status=status, executive_response=exec_resp, stage_results=tuple(stage_results))
        
        # 1. Semantic Parse
        self.event_bus.publish("SemanticParsingStarted", "orchestrator")
        t0 = time.monotonic()
        semantic_query = self.semantic_parser.parse(state.goal.query, intent=state.classification.intent)
        dur = (time.monotonic() - t0) * 1000
        
        if not semantic_query.topics and not semantic_query.keywords:
            add_stage("Semantic Parser", "FAIL", "User Query", "SemanticQuery", "UNKNOWN", dur, {"Topics": "UNKNOWN"}, "Parser returned no topics or keywords")
            return abort_with_error("Semantic Parser", "Parser returned no topics or keywords", {}, ExecutionStatus.RUNTIME_FAILURE)
            
        add_stage("Semantic Parser", "PASS", "User Query", "SemanticQuery", f"Topics: {semantic_query.topics}, Keywords: {semantic_query.keywords}", dur, {})
        state = dataclasses.replace(state, semantic_query=semantic_query)

        # 2. Goal Graph
        self.event_bus.publish("GoalGraphStarted", "orchestrator")
        t0 = time.monotonic()
        goal_graph = self.goal_graph_builder.build(semantic_query)
        dur = (time.monotonic() - t0) * 1000
        if not goal_graph.nodes:
            add_stage("Goal Graph", "FAIL", "SemanticQuery", "GoalGraph", "0 goals", dur, {}, "No executable goals extracted")
            return abort_with_error("Goal Graph", "No executable goals extracted from semantic query", {}, ExecutionStatus.RUNTIME_FAILURE)
        add_stage("Goal Graph", "PASS", "SemanticQuery", "GoalGraph", f"{len(goal_graph.nodes)} goals", dur, {"Hash": goal_graph.hash()})
        state = dataclasses.replace(state, goal_graph=goal_graph)
        
        # 3. Repository Knowledge wrapper
        adapter = PlatformResultAdapter(state.platform_result)
        repo_knowledge = RepositoryKnowledge(adapter)
        
        # 4. Entity Resolution
        self.event_bus.publish("EntityResolution", "orchestrator")
        semantic_query = self.entity_resolver.resolve(semantic_query, repo_knowledge)
        goal_graph = self.goal_graph_builder.build(semantic_query)
        state = dataclasses.replace(state, semantic_query=semantic_query, goal_graph=goal_graph)
        
        # 5. Capability Retrieval
        self.event_bus.publish("CapabilityRetrieval", "orchestrator")
        t0 = time.monotonic()
        candidates = self.retriever.retrieve(semantic_query, repo_knowledge)
        dur = (time.monotonic() - t0) * 1000
        
        diags = {"Candidates": len(candidates), "Details": [c.diagnostics for c in candidates if hasattr(c, 'diagnostics')]}
        if not candidates:
            add_stage("Capability Retrieval", "FAIL", "SemanticQuery", "CapabilityCandidates", "0 candidates", dur, diags, "No candidates found")
            return abort_with_error("Capability Retrieval", "No capability matched query", diags, ExecutionStatus.CAPABILITY_MISSING)
            
        add_stage("Capability Retrieval", "PASS", "SemanticQuery", "CapabilityCandidates", f"{len(candidates)} candidates", dur, diags)
        state = dataclasses.replace(state, candidate_set=candidates)
        
        # 6. Planning
        while not self.policy_engine.should_stop(state):
            self.event_bus.publish("PlannerStarted", "orchestrator", iteration=iteration)
            
            t0 = time.monotonic()
            actions, execution_graph, plan_diagnostics = self.planner.plan(candidates, semantic_query, goal_graph)
            dur = (time.monotonic() - t0) * 1000
            
            if not actions:
                add_stage("Planner", "FAIL", "Candidates, Query", "ExecutionPlan", "0 actions", dur, plan_diagnostics, "Planner selected zero capabilities")
                return abort_with_error("Planner", "Planner selected zero capabilities", plan_diagnostics, ExecutionStatus.RUNTIME_FAILURE)
                
            state = dataclasses.replace(state, execution_graph=execution_graph)
            for action in actions:
                self.event_bus.publish("CapabilitySelected", "planner", capability=action.tool, reason=action.reasoning)
            self.event_bus.publish(
                "PlannerFinished",
                "orchestrator",
                iteration=iteration,
                capabilities=[action.tool for action in actions],
                execution_nodes=len(execution_graph.nodes),
            )
            add_stage("Planner", "PASS", "GoalGraph, Candidates, Memory", "ExecutionGraph", f"{len(execution_graph.nodes)} nodes, {len(actions)} execution requests", dur, plan_diagnostics)
            
            self.event_bus.publish("ExecutionStarted", "orchestrator")
            t0 = time.monotonic()
            from .models import ExecutionRequest
            requests = [ExecutionRequest(capability=a.tool, arguments=a.arguments, cacheable=True) for a in actions]
            observations = self.executor.execute_queue(requests, state.platform_result)
            repo_mem = dataclasses.replace(state.repository_memory, observations=list(state.repository_memory.observations) + observations)
            state = dataclasses.replace(
                state,
                repository_memory=repo_mem,
                tool_history=state.tool_history + tuple(a.tool for a in actions),
            )
            dur = (time.monotonic() - t0) * 1000
            
            successful_results = [
                obs for obs in observations
                if isinstance(obs.output, CapabilityResult)
                and obs.output.status == "SUCCESS"
                and obs.output.evidence_ids
            ]
            exec_diags = {
                "Requests": len(actions),
                "Successful Results": len(successful_results),
                "Failures": [
                    getattr(obs.output, "capability", obs.tool)
                    for obs in observations
                    if not (
                        isinstance(obs.output, CapabilityResult)
                        and obs.output.status == "SUCCESS"
                        and obs.output.evidence_ids
                    )
                ]
            }
            if not successful_results:
                add_stage("Executor", "FAIL", "ExecutionPlan", "CapabilityResults", "0 successful results", dur, exec_diags, "No capabilities executed successfully")
                return abort_with_error("Executor", "No capabilities produced evidence.", exec_diags, ExecutionStatus.NO_EVIDENCE)
                
            add_stage("Executor", "PASS", "ExecutionGraph", "CapabilityResults", f"{len(successful_results)} evidence-bearing results", dur, exec_diags)
            self.event_bus.publish("MemoryUpdated", "orchestrator", observations=len(state.repository_memory.observations))
            
            # 7. Evaluate Loop
            iteration += 1
            state = dataclasses.replace(state, current_iteration=iteration)
            break
            
        # 8. Verification & Synthesis
        self.event_bus.publish("SynthesisStarted", "orchestrator")
        t0 = time.monotonic()
        report = self.answer_builder.build(state)
        dur = (time.monotonic() - t0) * 1000
        
        # Optional LLM rewrite
        confidence = AnswerConfidence(1.0, 1.0, 1.0, 1.0, 1.0)
        exec_resp = self.synthesizer.synthesize(report, state.classification.intent, confidence)
        
        # Verify
        from .verifier import EvidenceVerificationEngine
        verifier = EvidenceVerificationEngine()
        claims = self.answer_builder.extract_verified_claims(state)
        verification = verifier.verify(exec_resp.technical_summary, claims, state.repository_memory.observations)

        add_stage("Verifier", "PASS", "CapabilityResults", "VerifiedClaims", f"{verification.verified_claims} claims", dur, {})
        
        self.invariant_checker.validate(state)
        
        if state.classification.intent == Intent.REPOSITORY_QUERY and verification.verified_claims == 0:
            add_stage("Verifier", "FAIL", "CapabilityResults", "VerifiedClaims", "0 claims", dur, {}, "Zero verified claims")
            return abort_with_error("Verifier", "Verification Engine failed to verify any claims against evidence.", {}, ExecutionStatus.VERIFICATION_FAILED)
            
        self._print_health_matrix(stage_results)
        
        total_claims = max(len(verification.critiques), 1)
        verified_claims = verification.verified_claims
        evidence_results = [
            obs for obs in state.repository_memory.observations
            if isinstance(obs.output, CapabilityResult)
            and obs.output.status == "SUCCESS"
            and obs.output.evidence_ids
        ]
        confidence = AnswerConfidence(
            evidence_coverage=1.0 if evidence_results else 0.0,
            verification_score=verified_claims / total_claims,
            planner_completion=len(evidence_results) / max(len(state.tool_history), 1),
            reflection_score=1.0 if not state.reflection or not state.reflection.contradictions else 0.5,
            reasoning_consistency=1.0,
        )
        answer = CognitiveAnswer(
            query=state.goal.query,
            response=verification.verified_text,
            verification=verification,
        )
        exec_resp = dataclasses.replace(
            exec_resp,
            executive_summary=verification.verified_text,
            technical_summary=verification.verified_text,
            supporting_evidence=[
                evidence_id
                for obs in evidence_results
                for evidence_id in obs.output.evidence_ids
            ],
            confidence=confidence.overall,
        )
        self.event_bus.publish("AnswerFinished", "orchestrator", confidence=confidence.overall)

        state = dataclasses.replace(
            state,
            status=ExecutionStatus.SUCCESS,
            executive_response=exec_resp,
            answer=answer,
            confidence=confidence,
            stage_results=tuple(stage_results),
        )
        return state

    def _print_health_matrix(self, stage_results):
        print("\n")
        print("="*60)
        print("                   RUNTIME HEALTH MATRIX                    ")
        print("="*60)
        total_time = 0.0
        for sr in stage_results:
            color = "\033[92m" if sr.status == "PASS" else "\033[91m"
            reset = "\033[0m"
            print(f"{sr.stage_name:<25} {color}[{sr.status}]{reset} {sr.duration_ms:>10.1f}ms")
            if sr.status == "FAIL":
                print(f"   Reason: {sr.reason}")
            total_time += sr.duration_ms
        print("-" * 60)
        print(f"{'Total':<25} {'':>6} {total_time:>10.1f}ms")
        print("=" * 60)
        print("\n")
