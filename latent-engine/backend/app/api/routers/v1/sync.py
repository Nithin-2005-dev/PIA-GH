"""
Sync Engine REST API.

Exposes sync control and status to the Developer Console.
All state is served from the Operational Store and Sync Engine — never computed on the fly.
"""
from __future__ import annotations
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/sync", tags=["Sync Engine"])


class SyncRequest(BaseModel):
    repository: str
    mode: str = "incremental"   # full | incremental | replay_dataset | rebuild_projections
    branch: str = "main"
    commit_limit: int = 100
    github_token: Optional[str] = None
    workspace_id: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    repository: str
    sync_mode: str
    status: str
    started_at: str


class SyncJobDTO(BaseModel):
    job_id: str
    repository: str
    workspace_id: Optional[str]
    sync_mode: str
    status: str
    started_at: str
    completed_at: Optional[str]
    error: Optional[str]
    progress: Dict[str, int]


class CancelResponse(BaseModel):
    job_id: str
    status: str


class ActiveJobsResponse(BaseModel):
    jobs: List[SyncJobDTO]


class SyncHistoryResponse(BaseModel):
    jobs: List[SyncJobDTO]


class RateLimitResponse(BaseModel):
    remaining: int
    limit: int
    reset_at: int


def _job_dto(job) -> SyncJobDTO:
    return SyncJobDTO(
        job_id=job.job_id,
        repository=job.repository,
        workspace_id=job.workspace_id,
        sync_mode=job.sync_mode.value,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error,
        progress=job.progress
    )


@router.post("/start", response_model=JobResponse)
async def start_sync(request: SyncRequest):
    """Start a sync job. Returns job_id immediately; poll /sync/job/{job_id} for status."""
    from app.platform.sync_engine import get_sync_engine, SyncMode
    engine = get_sync_engine()
    try:
        mode = SyncMode(request.mode)
    except ValueError:
        raise HTTPException(400, detail=f"Invalid sync mode: {request.mode}. Choose from: full, incremental, replay_dataset, rebuild_projections")
    
    job = await engine.sync(
        repository=request.repository,
        mode=mode,
        branch=request.branch,
        commit_limit=request.commit_limit,
        github_token=request.github_token,
        workspace_id=request.workspace_id,
    )
    return JobResponse(
        job_id=job.job_id,
        repository=job.repository,
        sync_mode=job.sync_mode.value,
        status=job.status.value,
        started_at=job.started_at,
    )


@router.get("/job/{job_id}", response_model=SyncJobDTO)
async def get_job_status(job_id: str):
    """Sync Explorer: full job status with progress counters."""
    from app.platform.sync_engine import get_sync_engine
    engine = get_sync_engine()
    job = engine.get_job(job_id)
    if not job:
        # Check history
        history = engine.get_history(limit=100)
        job = next((j for j in history if j.job_id == job_id), None)
    if not job:
        raise HTTPException(404, detail=f"Job {job_id} not found")
    return _job_dto(job)


@router.post("/cancel/{job_id}", response_model=CancelResponse)
async def cancel_job(job_id: str):
    from app.platform.sync_engine import get_sync_engine
    engine = get_sync_engine()
    cancelled = await engine.cancel(job_id)
    if not cancelled:
        raise HTTPException(404, detail=f"Job {job_id} not found or not running")
    return CancelResponse(job_id=job_id, status="cancellation_requested")


@router.get("/active", response_model=ActiveJobsResponse)
async def get_active_jobs():
    """Live running sync jobs."""
    from app.platform.sync_engine import get_sync_engine
    engine = get_sync_engine()
    return ActiveJobsResponse(jobs=[_job_dto(j) for j in engine.get_active_jobs()])


@router.get("/history", response_model=SyncHistoryResponse)
async def get_sync_history(limit: int = 20):
    """Completed sync jobs."""
    from app.platform.sync_engine import get_sync_engine
    engine = get_sync_engine()
    return SyncHistoryResponse(jobs=[_job_dto(j) for j in engine.get_history(limit)])


@router.get("/rate-limit", response_model=RateLimitResponse)
async def get_rate_limit(github_token: Optional[str] = None):
    """Current GitHub API rate limit status."""
    from app.platform.sync_engine import GitHubSourcePlugin
    plugin = GitHubSourcePlugin(token=github_token)
    r = plugin.get_rate_limit()
    return RateLimitResponse(remaining=r.get("remaining", 0), limit=r.get("limit", 0), reset_at=r.get("reset_at", 0))
