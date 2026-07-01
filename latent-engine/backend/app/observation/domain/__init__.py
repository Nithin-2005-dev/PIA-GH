from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.domain.entity_ref import EntityRef


class ObservationType(Enum):
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    REVIEW = "review"
    COMMENT = "comment"
    MERGE = "merge"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    INCIDENT = "incident"
    RELEASE = "release"
    RUNTIME = "runtime"
    SECURITY = "security"
    TEST = "test"
    CLOUD = "cloud"
    INFRASTRUCTURE = "infrastructure"
    AI_SYSTEM = "ai_system"
    DOCUMENTATION = "documentation"


class ObservationCategory(Enum):
    SOURCE_CONTROL = "source_control"
    CODE_REVIEW = "code_review"
    CI_CD = "ci_cd"
    RUNTIME = "runtime"
    SECURITY = "security"
    TESTING = "testing"
    CLOUD = "cloud"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    AI = "ai"
    PROJECT_MANAGEMENT = "project_management"


class ObservationLifecycle(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ObservationProvenance:
    source_platform: str
    source_adapter: str
    source_record_id: str
    fetched_at: datetime | None = None
    adapter_version: str = "1.0"
    replay_ref: str | None = None


@dataclass(frozen=True)
class ObservationContext:
    repository: str | None = None
    organization: str | None = None
    branch: str | None = None
    tenant_id: str | None = None
    labels: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FileChangeFacts:
    path: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    previous_path: str | None = None
    patch: str | None = None


@dataclass(frozen=True)
class CommitFacts:
    commit_id: str
    message: str
    author_name: str | None
    author_email: str | None
    authored_at: datetime
    committer_name: str | None = None
    committer_email: str | None = None
    committed_at: datetime | None = None
    parent_ids: tuple[str, ...] = ()
    total_additions: int = 0
    total_deletions: int = 0
    total_changes: int = 0
    files: tuple[FileChangeFacts, ...] = ()
    signature_verified: bool | None = None


@dataclass(frozen=True)
class PullRequestFacts:
    pull_request_id: str
    title: str
    state: str
    author: str | None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    commit_ids: tuple[str, ...] = ()
    changed_files: int | None = None


@dataclass(frozen=True)
class IssueFacts:
    issue_id: str
    title: str
    state: str
    author: str | None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewFacts:
    review_id: str
    subject_id: str
    reviewer: str | None
    state: str
    submitted_at: datetime | None = None
    comment_count: int = 0


@dataclass(frozen=True)
class CommentFacts:
    comment_id: str
    subject_id: str
    author: str | None
    body: str
    created_at: datetime
    updated_at: datetime | None = None


@dataclass(frozen=True)
class MergeFacts:
    merge_id: str
    source_ref: str
    target_ref: str
    merged_by: str | None
    merged_at: datetime
    commit_id: str | None = None


@dataclass(frozen=True)
class BuildFacts:
    build_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True)
class DeploymentFacts:
    deployment_id: str
    environment: str
    status: str
    deployed_at: datetime
    version: str | None = None


@dataclass(frozen=True)
class IncidentFacts:
    incident_id: str
    title: str
    severity: str
    status: str
    started_at: datetime
    resolved_at: datetime | None = None
    service: str | None = None


@dataclass(frozen=True)
class ReleaseFacts:
    release_id: str
    version: str
    status: str
    released_at: datetime
    author: str | None = None


@dataclass(frozen=True)
class RuntimeFacts:
    runtime_id: str
    observed_at: datetime
    service: str
    status: str
    counters: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class SecurityFacts:
    finding_id: str
    scanner: str
    observed_at: datetime
    category: str
    state: str
    affected_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class TestFacts:
    test_run_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    passed: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class CloudFacts:
    resource_id: str
    resource_type: str
    observed_at: datetime
    state: str
    region: str | None = None


@dataclass(frozen=True)
class InfrastructureFacts:
    resource_id: str
    resource_type: str
    observed_at: datetime
    state: str
    location: str | None = None


@dataclass(frozen=True)
class DocumentationFacts:
    document_id: str
    path: str
    observed_at: datetime
    state: str
    title: str | None = None


@dataclass(frozen=True)
class AISystemFacts:
    system_id: str
    observed_at: datetime
    provider: str
    model: str
    state: str


CanonicalFacts = (
    CommitFacts
    | PullRequestFacts
    | IssueFacts
    | ReviewFacts
    | CommentFacts
    | MergeFacts
    | BuildFacts
    | DeploymentFacts
    | IncidentFacts
    | ReleaseFacts
    | RuntimeFacts
    | SecurityFacts
    | TestFacts
    | CloudFacts
    | InfrastructureFacts
    | DocumentationFacts
    | AISystemFacts
)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    trace_id: str
    correlation_id: str
    timestamp: datetime
    observation_type: ObservationType
    observation_category: ObservationCategory
    source_platform: str
    source_adapter: str
    version: str
    lifecycle: ObservationLifecycle
    actors: tuple[EntityRef, ...]
    targets: tuple[EntityRef, ...]
    provenance: ObservationProvenance
    context: ObservationContext
    facts: CanonicalFacts
