"""Probe real PlatformRuntime to understand context structure."""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.platform.runtime import PlatformRuntime

print('Running PlatformRuntime on facebook/react (10 commits)...')
t0 = time.monotonic()
platform = PlatformRuntime.create()
result = platform.run(repository='facebook/react', commits=10, branch='main')
elapsed = time.monotonic() - t0
ctx = result.context

print(f'Completed in {elapsed:.1f}s')
print(f'Stages: {len(result.completed_stages)}')
print(f'Errors: {result.errors}')
print()

def safe_len(obj):
    try: return len(obj)
    except: return '?'

def safe_attrs(obj, n=10):
    try: return [a for a in dir(obj) if not a.startswith('_')][:n]
    except: return []

print('=== Context Contents ===')
print(f'observations      : {type(ctx.observations).__name__} len={safe_len(ctx.observations)}')
print(f'measurements      : {type(ctx.measurements).__name__} len={safe_len(ctx.measurements)}')
if ctx.measurements:
    m = ctx.measurements[0]
    print(f'  sample type     : {type(m).__name__}')
    print(f'  sample attrs    : {safe_attrs(m)}')
    # try to get metric name / value
    for attr in ['metric_name', 'name', 'key', 'label', 'value', 'score', 'metric', 'kind']:
        if hasattr(m, attr):
            print(f'  .{attr}         = {getattr(m, attr)}')

print(f'evidence_package  : {type(ctx.evidence_package).__name__}')
if ctx.evidence_package:
    print(f'  attrs           : {safe_attrs(ctx.evidence_package)}')
    for attr in ['items', 'observations', 'entries', 'evidence', 'data']:
        if hasattr(ctx.evidence_package, attr):
            val = getattr(ctx.evidence_package, attr)
            print(f'  .{attr} type={type(val).__name__} len={safe_len(val)}')

print(f'expertise_models  : {type(ctx.expertise_models).__name__} len={safe_len(ctx.expertise_models)}')
if ctx.expertise_models:
    e = ctx.expertise_models[0]
    print(f'  sample type     : {type(e).__name__}')
    print(f'  sample attrs    : {safe_attrs(e)}')

print(f'knowledge         : {type(ctx.knowledge).__name__} len={safe_len(ctx.knowledge)}')
if ctx.knowledge:
    k = ctx.knowledge[0]
    print(f'  sample type     : {type(k).__name__}')
    print(f'  sample attrs    : {safe_attrs(k)}')

print(f'knowledge_graph   : {type(ctx.knowledge_graph).__name__ if ctx.knowledge_graph else "None"}')
if ctx.knowledge_graph:
    print(f'  attrs           : {safe_attrs(ctx.knowledge_graph)}')
    for attr in ['nodes', 'edges', 'vertices', 'relationships']:
        if hasattr(ctx.knowledge_graph, attr):
            val = getattr(ctx.knowledge_graph, attr)
            print(f'  .{attr} len={safe_len(val)}')

print(f'reasoning_results : {type(ctx.reasoning_results).__name__} len={safe_len(ctx.reasoning_results)}')
if ctx.reasoning_results:
    r = ctx.reasoning_results[0]
    print(f'  sample type     : {type(r).__name__}')
    print(f'  sample attrs    : {safe_attrs(r)}')

print(f'org_intelligence  : {type(ctx.org_intelligence).__name__ if ctx.org_intelligence else "None"}')
if ctx.org_intelligence:
    print(f'  attrs           : {safe_attrs(ctx.org_intelligence)}')

print()
print('=== Stage Timings ===')
for stage in result.completed_stages:
    print(f'  {stage.module:<15} {stage.name:<30} {stage.duration*1000:.1f}ms errors={stage.errors}')
