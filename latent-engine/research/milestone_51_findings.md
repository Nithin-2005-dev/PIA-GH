# Milestone 51 Findings

## Audit Findings

The platform had two execution paths:

- Runtime infrastructure in `app.platform`
- Showcase orchestration in `scripts.platform_showcase`

The showcase path directly owned stage ordering and directly constructed some
business services. The most visible duplicates were measurement/evidence
construction, NetworkX graph construction, and organization intelligence over a
showcase-specific graph shape.

## Consolidation Findings

`PlatformRuntime` can now execute a canonical pipeline through `run(...)`.
Module registration and dependency order are the source of execution truth.

The showcase has been reduced to presentation:

- load CLI/environment config
- call `PlatformRuntime.run(...)`
- subscribe to runtime stage events
- render final summary

## Canonical Services

Measurement uses `MeasurementEngine` from DI.

Evidence uses `EvidenceSynthesisEngine` from DI.

Graph construction uses `KnowledgeGraphBuilder.build_from_models(...)` from DI.

Organization intelligence accepts the canonical `OrganizationalGraph` node
shape and keeps NetworkX support only for historical replay compatibility.

## Verification

Added `backend/scripts/test_m51_platform_runtime_unification.py`.

The test proves:

- `PlatformRuntime.run(...)` is the entry point
- default modules are registered by runtime
- dependency-ordered stage bindings execute automatically
- runtime events propagate
- stage contracts are recorded
- lineage of completed stage modules is deterministic

Existing runtime and DI migration smoke tests were updated and continue to pass.

## Remaining Work

Several historical scripts still instantiate domain services directly for
focused examples or legacy tests. They should either become runtime-based tests
or be explicitly classified as service unit tests. The next cleanup pass should
move organization intelligence computations out of showcase stage code into a
first-class service with the current stage reduced to rendering only.
