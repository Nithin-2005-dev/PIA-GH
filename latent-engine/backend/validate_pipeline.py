"""
PIA Reality Check Validation Script.
Runs the full pipeline against facebook/react and produces an honest report.
No mocking. No fabrication. Reports 0s as 0s.
"""
import asyncio
import json
import time
import datetime

def hr(title=""):
    print()
    print("=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def section(title):
    print()
    print(f"--- {title} ---")

# --- Phase A: Sync Pipeline -------------------------------

async def phase_a_sync():
    hr("PHASE A — Sync Pipeline Validation")
    from app.platform.sync_engine import get_sync_engine, SyncMode, GitHubSourcePlugin
    from app.platform.projections.engine import get_projection_engine
    from app.adapters.database.sqlite_provider import get_provider

    # First check rate limit
    section("GitHub Rate Limit Check")
    plugin = GitHubSourcePlugin(token=None)
    rl = plugin.get_rate_limit()
    print(f"  Rate limit remaining : {rl.get('remaining', 'unknown')}")
    print(f"  Rate limit total     : {rl.get('limit', 'unknown')}")
    if rl.get('remaining', 0) < 10:
        print("  WARNING: Rate limit too low. Using small commit limit.")
        commit_limit = 10
    else:
        commit_limit = 30   # keep it deterministic and fast for validation

    section(f"Fetching facebook/react (last {commit_limit} commits, no token)")
    engine = get_sync_engine()
    t0 = time.monotonic()

    job = await engine.sync(
        repository="facebook/react",
        mode=SyncMode.FULL,
        branch="main",
        commit_limit=commit_limit,
        github_token=None,
    )

    # Wait for job to complete (it runs as a background task)
    for _ in range(120):  # max 2 min
        await asyncio.sleep(1)
        # Re-check job from history since active jobs get moved there
        active = engine.get_active_jobs()
        if not any(j.job_id == job.job_id for j in active):
            break
    
    elapsed = time.monotonic() - t0

    # Find completed job
    history = engine.get_history(limit=10)
    completed_job = next((j for j in history if j.job_id == job.job_id), job)

    section("Sync Results")
    print(f"  Status               : {completed_job.status.value}")
    print(f"  Duration             : {elapsed:.1f}s")
    print(f"  Commits requested    : {commit_limit}")
    print(f"  Commits processed    : {completed_job.commits_processed}")
    print(f"  Developers found     : {completed_job.developers_found}")
    print(f"  Files processed      : {completed_job.files_processed}")
    print(f"  Objects added        : {completed_job.objects_added}")
    print(f"  Objects updated      : {completed_job.objects_updated}")
    print(f"  API calls made       : {completed_job.api_calls_made}")
    print(f"  Last commit SHA      : {completed_job.last_commit_sha[:12] if completed_job.last_commit_sha else 'none'}")
    if completed_job.error:
        print(f"  ERROR                : {completed_job.error}")

    return completed_job


# --- Phase B: Operational Store Validation ---------------

def phase_b_store():
    hr("PHASE B — Operational Store Validation")
    from app.adapters.database.sqlite_provider import get_provider
    from app.adapters.database.models import (
        WorkspaceRecord, RepositorySessionRecord, CommitRecord,
        DeveloperRecord, FileRecord, MeasurementRecord,
        EvidenceRecord, ExecutionRecord, ReasoningRecord, DatasetRecord
    )

    provider = get_provider()
    counts = {}
    tables = [
        ("Workspaces",          WorkspaceRecord),
        ("Repository Sessions", RepositorySessionRecord),
        ("Commits",             CommitRecord),
        ("Developers",          DeveloperRecord),
        ("Files",               FileRecord),
        ("Measurements",        MeasurementRecord),
        ("Evidence",            EvidenceRecord),
        ("Executions",          ExecutionRecord),
        ("Reasoning Results",   ReasoningRecord),
        ("Datasets",            DatasetRecord),
    ]

    section("Object Counts")
    all_zero = True
    for label, model in tables:
        n = provider.count(model)
        counts[label] = n
        status = "[OK]" if n > 0 else "[ ] (empty)"
        if n > 0:
            all_zero = False
        print(f"  {label:<25} : {n:>6}  {status}")

    if all_zero:
        print("\n  CRITICAL: All tables are empty — sync did not persist data.")
    else:
        print(f"\n  Total records: {sum(counts.values())}")

    # Show sample commits
    section("Sample Commits (first 3)")
    commits = provider.query(CommitRecord, limit=3)
    if commits:
        for c in commits:
            print(f"  sha={c.sha[:10]}  author={c.author_name:<20}  msg={c.message[:50]}")
    else:
        print("  NONE — commits table is empty")

    # Show sample developers
    section("Sample Developers (first 5)")
    devs = provider.query(DeveloperRecord, limit=5)
    if devs:
        for d in devs:
            print(f"  {d.email:<35}  commits={d.commit_count}")
    else:
        print("  NONE — developer table is empty")

    return counts


# --- Phase C: Projection Validation ----------------------

async def phase_c_projections():
    hr("PHASE C — Projection Validation")
    from app.platform.projections.engine import get_projection_engine
    from app.platform.projections.registry import get_projection_registry

    engine = get_projection_engine()

    # Trigger a rebuild so we have fresh data
    section("Triggering rebuild-all after sync")
    t0 = time.monotonic()
    results = await engine.rebuild_all()
    elapsed = (time.monotonic() - t0) * 1000

    section("Projection Results")
    for r in results:
        status = "[OK]" if r.success else "[FAIL] FAILED"
        print(f"  {r.projection_id:<30} : {status}")
        print(f"    duration_ms  = {r.duration_ms:.1f}")
        print(f"    record_count = {r.record_count}")
        print(f"    node_count   = {r.node_count}")
        if r.error:
            print(f"    error        = {r.error[:120]}")

    section("Projection Status")
    status = engine.get_status()
    for pid, info in status.items():
        print(f"  {pid:<30} : {info['status']}")
        print(f"    last_built   = {info['last_built_at']}")
        print(f"    record_count = {info['record_count']}")
        metrics = info.get('metrics', {})
        print(f"    exec_count   = {metrics.get('execution_count', 0)}")
        print(f"    avg_latency  = {metrics.get('avg_latency_ms', 0):.1f}ms")

    section("Impact Simulation: what changes if 'measurement' changes?")
    impact = engine.simulate_impact("measurement")
    print(f"  Affected projections: {impact['affected_projections']}")

    return results


# --- Phase D: End-to-End Query Trace ---------------------

def phase_d_query():
    hr("PHASE D — End-to-End Query Trace")
    from app.api.services.query_service import QueryService
    from app.adapters.database.sqlite_provider import get_provider
    from app.adapters.database.models import ExecutionRecord

    provider = get_provider()
    svc = QueryService()

    query = "Who is the top contributor to facebook/react?"
    section(f"Query: {query!r}")

    t0 = time.monotonic()
    try:
        result = svc.execute_query(query=query, workspace_id="facebook/react")
        elapsed = (time.monotonic() - t0) * 1000
        print(f"  Status           : {result.status}")
        print(f"  Total latency    : {elapsed:.0f}ms")
        print(f"  Answer           : {result.answer[:200]}")
        print(f"  Reasoning events : {len(result.reasoning_trace)}")
        for t in result.reasoning_trace:
            print(f"    [{t.stage}] {t.execution_time_ms:.1f}ms : {t.decision[:60]}")
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        print(f"  ERROR ({elapsed:.0f}ms): {e}")


# --- Phase E: Object Lineage Check -----------------------

def phase_e_lineage():
    hr("PHASE E — Object Lineage Validation")
    from app.adapters.database.sqlite_provider import get_provider
    from app.adapters.database.models import DeveloperRecord, CommitRecord
    from app.platform.events.store import get_event_store

    provider = get_provider()
    event_store = get_event_store()

    devs = provider.query(DeveloperRecord, limit=1)
    if not devs:
        print("  SKIP: No developers in Operational Store — sync must complete first.")
        return

    dev = devs[0]
    section(f"Developer: {dev.email}")
    print(f"  object_id     : {dev.identity.object_id}")
    print(f"  workspace_id  : {dev.identity.workspace_id}")
    print(f"  execution_id  : {dev.identity.execution_id}")
    print(f"  version       : {dev.identity.version}")
    print(f"  created_at    : {dev.identity.created_at}")

    # Check events for this developer
    events = event_store.get_events_for_object(dev.identity.object_id, limit=5)
    section("Events touching this developer")
    if events:
        for e in events:
            print(f"  [{e.event_type}] {e.occurred_at} source={e.source_component}")
    else:
        print("  NONE — no events recorded for this developer object_id")
        print("  (expected: developer.ingested event with this object_id)")


# --- Phase F: Event Replay Validation --------------------

async def phase_f_replay():
    hr("PHASE F — Event Replay Validation")
    from app.platform.projections.engine import get_projection_engine
    from app.platform.events.store import get_event_store

    event_store = get_event_store()
    engine = get_projection_engine()

    section("Event Store Statistics")
    total = event_store.count()
    print(f"  Total events in log: {total}")

    from app.platform.events.store import EventType
    event_types = [
        EventType.SYNC_STARTED.value,
        EventType.SYNC_COMPLETED.value,
        EventType.COMMIT_INGESTED.value,
        EventType.DEVELOPER_INGESTED.value,
        EventType.FILE_INGESTED.value,
        EventType.PROJECTION_BUILD_STARTED.value,
        EventType.PROJECTION_BUILD_COMPLETED.value,
        EventType.SYSTEM_STARTED.value,
    ]
    for et in event_types:
        n = event_store.count([et])
        print(f"  {et:<40} : {n}")

    # Invalidate all projections then replay
    section("Invalidating all projections")
    from app.platform.projections.registry import get_projection_registry
    registry = get_projection_registry()
    for p in registry.list_all():
        await engine.invalidate(p.projection_id)
        print(f"  Invalidated: {p.projection_id} → status=stale")

    section("Replaying from event store")
    t0 = time.monotonic()
    replay_results = await engine.replay()
    elapsed = (time.monotonic() - t0) * 1000
    print(f"  Replay duration: {elapsed:.1f}ms")
    print(f"  Projections rebuilt: {len(replay_results)}")
    for r in replay_results:
        status = "[OK]" if r.success else "[FAIL]"
        print(f"  {status} {r.projection_id}: {r.record_count} records, {r.duration_ms:.1f}ms")


# --- Phase G: Console Data Source Audit ------------------

def phase_g_console_audit():
    hr("PHASE G — Console Data Source Audit")
    print("""
  Widget                        Data Source          Status
  -------------------------------------------------------------
  Knowledge Graph               KnowledgeGraphProj   STUB (no real nodes yet)
  Runtime Inspector             WebSocket events     MOCKED (no live stream)
  Pipeline Timeline             WebSocket events     MOCKED (no live stream)
  Explainability View           ExecutionRecord      PARTIAL (exec logs missing)
  Benchmark Center              BenchmarkProjection  STUB (no real benchmarks)
  Query Playground              QueryService         LIVE (real pipeline)
  Database Inspector            OperationalStore     LIVE (real data via /store)
  Projection Status             ProjectionRegistry   LIVE (real via /registry)
  Algorithm Explorer            AlgorithmRegistry    LIVE (5 algorithms)
  Sync Explorer                 SyncEngine           LIVE (real job tracking)
  Repository Explorer           OperationalStore     NOT IMPLEMENTED
  Measurement Explorer          MeasurementRecord    EMPTY (no measurements yet)
  Evidence Explorer             EvidenceRecord       EMPTY (no evidence yet)
  Rule Explorer                 RuleRegistry         NOT IMPLEMENTED
  Failure Explorer              EventStore           NOT IMPLEMENTED
  Universal Object Explorer     Store /search        LIVE (but no data)
  Ctrl+K Search                 Store /search        LIVE (but no data)
  """)


# --- Main -------------------------------------------------

async def main():
    print()
    print("=" * 60)
    print("  PIA REALITY CHECK — Full Pipeline Validation")
    print(f"  {datetime.datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    completed_job = await phase_a_sync()
    counts = phase_b_store()
    await phase_c_projections()
    phase_d_query()
    phase_e_lineage()
    await phase_f_replay()
    phase_g_console_audit()

    hr("SUMMARY")
    core_infra = sum(counts.values()) > 0
    print(f"  Core Infrastructure:  {'[OK] PASS' if core_infra else '[FAIL] FAIL — store empty'}")
    print(f"  Sync completed:       {'[OK] PASS' if completed_job.commits_processed > 0 else '[FAIL] FAIL — no commits ingested'}")
    print(f"  Commits ingested:     {counts.get('Commits', 0)}")
    print(f"  Developers ingested:  {counts.get('Developers', 0)}")
    print(f"  Files ingested:       {counts.get('Files', 0)}")
    print(f"  Measurements:         {counts.get('Measurements', 0)} (expected: 0 — not yet generated)")
    print(f"  Evidence:             {counts.get('Evidence', 0)} (expected: 0 — not yet generated)")
    print()
    print("  GAPS TO ADDRESS:")
    if counts.get('Measurements', 0) == 0:
        print("  - No measurements generated from commit data (Phase next)")
    if counts.get('Evidence', 0) == 0:
        print("  - No evidence synthesized (requires measurement step)")
    print("  - Projections contain 0 nodes (stub builders — needs real projection logic)")
    print("  - Runtime Inspector / Timeline are still mocked in frontend")
    print("  - Measurement, Evidence, Rule Explorers not implemented")


asyncio.run(main())
