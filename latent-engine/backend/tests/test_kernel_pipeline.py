import pytest
from app.kernel.context import ExecutionContext
from app.kernel.models import RepositoryMemory
from app.kernel.registry import CapabilityDefinition, CapabilityHealth
from app.kernel.scheduler import Job
from app.kernel.core_runtime import KernelRuntime

def test_kernel_phase1_pipeline():
    # 1. Initialize Context
    memory = RepositoryMemory()
    context = ExecutionContext.create_default(session_id="test_session", memory=memory)
    
    # 2. Register Capability
    cap = CapabilityDefinition(
        id="cap_test_deterministic",
        version="1.0",
        description="A test deterministic capability",
        inputs={"param1": str},
        outputs={"result": bool},
        evidence_produced=["ev_test_1"],
        required_resources=["cpu"]
    )
    context.registry.register(cap)
    
    # 3. Plan & Schedule
    job1 = Job(id="job_1", capability_id="cap_test_deterministic", arguments={"param1": "test"})
    job2 = Job(id="job_2", capability_id="cap_test_deterministic", arguments={"param1": "test"}, dependencies=["job_1"])
    context.scheduler.submit(job1)
    context.scheduler.submit(job2)
    
    # 4. Execute Pipeline
    runtime = KernelRuntime(context)
    results = runtime.run_pipeline()
    
    # 5. Validate
    assert len(results) == 2
    assert results[0]["capability"] == "cap_test_deterministic"
    assert results[1]["capability"] == "cap_test_deterministic"
    assert context.scheduler._jobs["job_1"].status == "DONE"
    assert context.scheduler._jobs["job_2"].status == "DONE"
