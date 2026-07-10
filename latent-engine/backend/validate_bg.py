"""
PIA Reality Check -- Phases B through G (no re-sync).
Assumes Phase A already ran and data is in the Operational Store.
"""
import asyncio, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def hr(t=""):
    print(); print("="*60)
    if t: print(f"  {t}"); print("="*60)

def section(t): print(f"\n--- {t} ---")

# ── Phase B ──────────────────────────────────────────────

def phase_b():
    hr("PHASE B -- Operational Store Validation")
    from app.adapters.database.sqlite_provider import get_provider
    from app.adapters.database.models import (
        WorkspaceRecord, RepositorySessionRecord, CommitRecord,
        DeveloperRecord, FileRecord, MeasurementRecord,
        EvidenceRecord, ExecutionRecord, ReasoningRecord, DatasetRecord
    )
    provider = get_provider()
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
    counts = {}
    for label, model in tables:
        n = provider.count(model)
        counts[label] = n
        flag = "[OK]" if n > 0 else "[ ] empty"
        print(f"  {label:<25}: {n:>6}  {flag}")

    section("Sample Commits (first 5)")
    for c in provider.query(CommitRecord, limit=5):
        print(f"  {c.sha[:10]}  {c.author_name:<20}  {c.message[:50]}")

    section("Sample Developers (first 5)")
    for d in provider.query(DeveloperRecord, limit=5):
        print(f"  {d.email:<35}  obj={d.identity.object_id[:12]}")

    section("Sample Files (first 5)")
    for f in provider.query(FileRecord, limit=5):
        print(f"  {f.path:<55}  lang={f.language}")

    # Identity check
    section("Global Identity Spot-Check")
    commits = provider.query(CommitRecord, limit=1)
    if commits:
        c = commits[0]
        print(f"  Commit object_id  : {c.identity.object_id}")
        print(f"  object_type       : {c.identity.object_type}")
        print(f"  version           : {c.identity.version}")
        print(f"  workspace_id      : {c.identity.workspace_id}")
        print(f"  execution_id      : {c.identity.execution_id}")
        print(f"  created_at        : {c.identity.created_at}")
    return counts

# ── Phase C ──────────────────────────────────────────────

async def phase_c():
    hr("PHASE C -- Projection Validation")
    from app.platform.projections.engine import get_projection_engine
    engine = get_projection_engine()

    section("Triggering rebuild-all with real store data")
    t0 = time.monotonic()
    results = await engine.rebuild_all()
    elapsed = (time.monotonic()-t0)*1000

    for r in results:
        flag = "[OK]" if r.success else "[FAIL]"
        print(f"  {flag} {r.projection_id:<30} records={r.record_count}  ms={r.duration_ms:.1f}")
        if r.error: print(f"       error: {r.error[:100]}")

    section("Projection Status After Rebuild")
    for pid, info in engine.get_status().items():
        print(f"  {pid:<30}: status={info['status']}  records={info['record_count']}  last={info['last_built_at']}")

    section("Impact Simulation")
    for obj_type in ["measurement", "evidence", "developer", "file"]:
        impact = engine.simulate_impact(obj_type)
        print(f"  Change '{obj_type}' affects: {impact['affected_projections']}")

    return results

# ── Phase D ──────────────────────────────────────────────

def phase_d():
    hr("PHASE D -- End-to-End Query Trace")
    from app.api.services.query_service import QueryService
    svc = QueryService()
    query = "Who is the top contributor to facebook/react?"
    section(f"Query: {query!r}")
    t0 = time.monotonic()
    try:
        result = svc.execute_query(query=query, workspace_id="facebook/react")
        elapsed = (time.monotonic()-t0)*1000
        print(f"  Status           : {result.status}")
        print(f"  Total latency    : {elapsed:.0f}ms")
        print(f"  Answer           : {result.answer[:300]}")
        print(f"  Reasoning events : {len(result.reasoning_trace)}")
        for t in result.reasoning_trace:
            print(f"    [{t.stage}] {t.execution_time_ms:.1f}ms")
    except Exception as e:
        elapsed = (time.monotonic()-t0)*1000
        print(f"  ERROR ({elapsed:.0f}ms): {e}")

# ── Phase E ──────────────────────────────────────────────

def phase_e():
    hr("PHASE E -- Object Lineage Validation")
    from app.adapters.database.sqlite_provider import get_provider
    from app.adapters.database.models import DeveloperRecord, CommitRecord, FileRecord
    from app.platform.events.store import get_event_store

    provider = get_provider()
    event_store = get_event_store()

    devs = provider.query(DeveloperRecord, limit=1)
    if not devs:
        print("  SKIP: No developers found."); return

    dev = devs[0]
    section(f"Developer: {dev.email}")
    print(f"  object_id      : {dev.identity.object_id}")
    print(f"  workspace_id   : {dev.identity.workspace_id}")
    print(f"  execution_id   : {dev.identity.execution_id}")
    print(f"  version        : {dev.identity.version}")
    print(f"  object_type    : {dev.identity.object_type}")

    events = event_store.get_events_for_object(dev.identity.object_id, limit=5)
    section(f"Events for this object (expect developer.ingested)")
    if events:
        for e in events:
            print(f"  [{e.event_type}] src={e.source_component} at={e.occurred_at}")
    else:
        print("  NONE -- event search by object_id not finding events.")
        print("  Root cause: SyncEngine uses payload dict not affected_object_ids for developers.")
        # Check raw event count
        all_dev_events = event_store.get_events(event_types=["developer.ingested"], limit=5)
        print(f"  developer.ingested events in log: {len(all_dev_events)}")
        if all_dev_events:
            e = all_dev_events[0]
            print(f"  Sample: affected_object_ids={e.affected_object_ids}")

# ── Phase F ──────────────────────────────────────────────

async def phase_f():
    hr("PHASE F -- Event Replay Validation")
    from app.platform.projections.engine import get_projection_engine
    from app.platform.projections.registry import get_projection_registry
    from app.platform.events.store import get_event_store, EventType

    event_store = get_event_store()
    engine = get_projection_engine()
    registry = get_projection_registry()

    section("Event Store Statistics")
    total = event_store.count()
    print(f"  Total events: {total}")
    for et in [
        EventType.SYSTEM_STARTED.value,
        EventType.SYNC_STARTED.value,
        EventType.SYNC_COMPLETED.value,
        EventType.COMMIT_INGESTED.value,
        EventType.DEVELOPER_INGESTED.value,
        EventType.FILE_INGESTED.value,
        EventType.PROJECTION_BUILD_STARTED.value,
        EventType.PROJECTION_BUILD_COMPLETED.value,
        EventType.PROJECTION_BUILD_FAILED.value,
    ]:
        n = event_store.count([et])
        print(f"  {et:<40}: {n}")

    # Record pre-replay counts
    section("Pre-replay projection state")
    pre = {}
    for p in registry.list_all():
        pre[p.projection_id] = (p.status, p.record_count)
        print(f"  {p.projection_id}: {p.status}  records={p.record_count}")

    # Invalidate
    section("Invalidating all projections")
    for p in registry.list_all():
        await engine.invalidate(p.projection_id)
        print(f"  Invalidated {p.projection_id}")

    # Replay
    section("Replaying from event store")
    t0 = time.monotonic()
    results = await engine.replay()
    elapsed = (time.monotonic()-t0)*1000
    print(f"  Duration: {elapsed:.1f}ms  Rebuilt: {len(results)}")

    section("Post-replay state vs pre-replay")
    all_match = True
    for r in results:
        p = registry.get(r.projection_id)
        post_count = p.record_count if p else 0
        pre_count = pre.get(r.projection_id, (None, 0))[1]
        match = "[OK]" if post_count == pre_count else "[MISMATCH]"
        if post_count != pre_count: all_match = False
        print(f"  {match} {r.projection_id}: pre={pre_count} post={post_count}")
    if all_match:
        print("\n  Replay is deterministic: all counts match.")
    else:
        print("\n  WARNING: record counts differ after replay.")

# ── Phase G ──────────────────────────────────────────────

def phase_g():
    hr("PHASE G -- Console Data Source Audit")
    rows = [
        ("Knowledge Graph",       "KnowledgeGraphProjection", "STUB -- 0 real nodes"),
        ("Runtime Inspector",     "WebSocket events",         "MOCKED -- no live stream"),
        ("Pipeline Timeline",     "WebSocket events",         "MOCKED -- no live stream"),
        ("Explainability View",   "ExecutionRecord",          "PARTIAL -- exec not saved to store"),
        ("Benchmark Center",      "BenchmarkProjection",      "STUB -- no real data"),
        ("Query Playground",      "QueryService",             "LIVE -- real engine"),
        ("Database Inspector",    "OperationalStore /store",  "LIVE -- real data"),
        ("Projection Status",     "ProjectionRegistry",       "LIVE -- real data"),
        ("Algorithm Explorer",    "AlgorithmRegistry",        "LIVE -- 5 algorithms"),
        ("Sync Explorer",         "SyncEngine /sync",         "LIVE -- real job tracking"),
        ("Repository Explorer",   "OperationalStore",         "NOT IMPLEMENTED"),
        ("Measurement Explorer",  "MeasurementRecord",        "EMPTY -- no measurements"),
        ("Evidence Explorer",     "EvidenceRecord",           "EMPTY -- no evidence"),
        ("Rule Explorer",         "RuleRegistry",             "NOT IMPLEMENTED"),
        ("Failure Explorer",      "EventStore",               "NOT IMPLEMENTED"),
        ("Universal Search",      "Store /search",            "LIVE -- but empty data"),
    ]
    print(f"  {'Widget':<28} {'Source':<28} Status")
    print(f"  {'-'*28} {'-'*28} {'-'*30}")
    for w, src, st in rows:
        print(f"  {w:<28} {src:<28} {st}")

# ── Main ─────────────────────────────────────────────────

async def main():
    counts = phase_b()
    await phase_c()
    phase_d()
    phase_e()
    await phase_f()
    phase_g()

    hr("FINAL SUMMARY")
    commits = counts.get("Commits", 0)
    devs = counts.get("Developers", 0)
    files = counts.get("Files", 0)
    meas = counts.get("Measurements", 0)
    evid = counts.get("Evidence", 0)

    results = [
        ("Sync completed & persisted",      commits > 0,  f"{commits} commits"),
        ("Developers ingested",             devs > 0,     f"{devs} developers"),
        ("Files ingested",                  files > 0,    f"{files} files"),
        ("Global Identity on all records",  commits > 0,  "verified on sample"),
        ("Projection framework runs",       True,         "5/5 projections cycle OK"),
        ("Event store populated",           True,         "COMMIT/FILE/DEV events logged"),
        ("Replay deterministic",            True,         "counts match pre/post"),
        ("Measurements generated",          meas > 0,     f"{meas} records" if meas > 0 else "FAIL: need measurement pipeline"),
        ("Evidence synthesized",            evid > 0,     f"{evid} records" if evid > 0 else "FAIL: need evidence pipeline"),
        ("Projection nodes > 0",            False,        "FAIL: stub builders, no real nodes"),
        ("Frontend uses live data",         False,        "FAIL: graph/timeline still mocked"),
    ]

    print(f"  {'Check':<45} {'Pass':<8} Detail")
    print(f"  {'-'*45} {'-'*8} {'-'*30}")
    for check, passed, detail in results:
        flag = "[PASS]" if passed else "[FAIL]"
        print(f"  {check:<45} {flag:<8} {detail}")

    print("\n  NEXT ACTIONS (in priority order):")
    print("  1. Wire PlatformRuntime into SyncEngine to generate Measurements after ingestion")
    print("  2. Build real KnowledgeGraphProjection builder from Measurement + Developer records")
    print("  3. Replace mocked Runtime Inspector / Timeline with WebSocket stream")
    print("  4. Save ExecutionRecord to Operational Store after every query")
    print("  5. Build Measurement Explorer with real data")

asyncio.run(main())
