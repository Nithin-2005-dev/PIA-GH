import uuid
import time
from typing import Optional
from app.kernel.runtime import CognitiveRuntime
from app.kernel.models import AgentPolicy, ExecutionStatus, WorkspaceSession
from app.api.dtos.v1 import ExecutionTraceDTO_v1, TraceEventDTO_v1
from app.platform.core_modules import GitHubAdapterFactory
from app.kernel.provider_manager import ProviderManager
from app.kernel.provider import MockLLMProvider # In a full system, this could be the real LLM

class QueryService:
    def __init__(self):
        # In a real DI setup, we'd inject this
        pass

    def execute_query(self, query: str, workspace_id: str, dataset_version: str = "v1") -> ExecutionTraceDTO_v1:
        session_id = str(uuid.uuid4())
        query_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. Check Operational Store for recent execution
        from app.adapters.database.sqlite_provider import get_provider
        from app.adapters.database.models import ExecutionRecord, MeasurementRecord, EvidenceRecord, ReasoningRecord
        provider = get_provider()
        
        # Get the latest successful execution for this workspace
        executions = provider.query(
            ExecutionRecord, 
            filters={"workspace_id": workspace_id, "status": "success"}, 
            limit=1
        )
        # Note: In SQLiteProvider, we might need a custom query to sort by date descending.
        # But for now, we'll just check if any exists.
        
        platform_result = None
        if executions:
            latest_execution = executions[0]
            # Reconstruct PlatformResult context from DB records
            # This allows the query service to run completely decoupled from the runtime execution engine!
            from app.platform.api.contracts import RuntimePipelineResult
            from scripts.platform_showcase.context import PlatformContext
            
            # Fetch related records using IN queries or loops
            measurements = []
            for mid in latest_execution.measurement_ids:
                m = provider.get_by_id(MeasurementRecord, mid)
                if m: measurements.append(m)
                
            evidence = []
            for eid in latest_execution.evidence_ids:
                e = provider.get_by_id(EvidenceRecord, eid)
                if e: evidence.append(e)
                
            reasoning = []
            for rid in latest_execution.reasoning_ids:
                r = provider.get_by_id(ReasoningRecord, rid)
                if r: reasoning.append(r)
            
            # Create a lightweight context just for answering
            from pathlib import Path
            ctx = PlatformContext(
                repository=workspace_id, 
                branch="main", 
                commit_limit=0,
                github_token=None,
                tenant_id="default",
                output_directory=Path("outputs/showcase")
            )
            # Map canonical DB records back to domain objects or pass them as is.
            ctx.measurements = measurements
            ctx.evidence_package = evidence
            ctx.reasoning_results = reasoning
            
            platform_result = RuntimePipelineResult(
                context=ctx,
                completed_stages=(),
                execution_order=()
            )
        
        if platform_result is None:
            # Fall back to runtime if missing/stale
            from app.platform.runtime import PlatformRuntime
            platform = PlatformRuntime.create()
            platform_result = platform.run(repository=workspace_id, commits=50)

        # 2. Setup Cognitive Runtime
        from app.kernel.models import AgentPolicy
        policy = AgentPolicy()
        
        provider_mgr = ProviderManager(
            providers=[MockLLMProvider(latency_ms=10, token_rate=100)],
            policy=policy
        )
        runtime = CognitiveRuntime(provider_manager=provider_mgr, agent_policy=policy)
        
        # 3. Inject session contextual data
        from app.kernel.models import WorkspaceSession, CognitiveSession
        workspace = WorkspaceSession(repository=workspace_id)
        session = CognitiveSession(session_id=session_id, workspace_session=workspace)
        
        # 4. Run pipeline
        state = runtime.answer(platform_result=platform_result, question=query, session=session)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        trace_events = []
        if state.reasoning_trace:
            for t in state.reasoning_trace:
                trace_events.append(TraceEventDTO_v1(
                    stage=t.stage,
                    execution_time_ms=t.execution_time_ms,
                    decision=t.decision,
                    output_summary=t.output_summary,
                    cache_hit=t.cache_hit
                ))

        return ExecutionTraceDTO_v1(
            query_id=query_id,
            status=state.status.value,
            answer=state.answer.response if state.answer else (state.executive_response.summary if state.executive_response else "Execution completed without a text response."),
            reasoning_trace=trace_events,
            total_latency_ms=latency_ms
        )
