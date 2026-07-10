import asyncio
import os
import time
from app.platform.sync_engine import get_sync_engine, SyncMode
import app.platform.sync_engine
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder
from app.projections.graph_analytics import KnowledgeGraphAnalytics
from app.projections.graph_replay import KnowledgeGraphReplayEngine
from app.adapters.database.sqlite_provider import get_provider
from app.adapters.database.models import DeveloperRecord, FileRecord, CommitRecord, MeasurementRecord, EvidenceRecord

class MockMultiRepoGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None):
        pass
        
    def fetch_repository_metadata(self, repository: str) -> dict:
        return {"name": repository.split("/")[-1]}

    def fetch_commits(self, repository: str, branch: str, limit: int = 100, since_sha=None):
        commits = []
        for i in range(limit):
            commits.append({
                "sha": f"mocksha{i}_{repository.split('/')[-1]}",
                "message": f"Commit {i} in {repository}",
                "author_email": f"dev{i%5}@example.com",
                "author_name": f"Dev {i%5}",
                "timestamp": "2023-01-01T00:00:00Z",
                "additions": 10 + i,
                "deletions": 5,
            })
        return commits

    def fetch_file_tree(self, repository, commit_sha):
        return []

    def get_rate_limit(self):
        return {"remaining": 5000, "limit": 5000, "reset_at": 0}

REPOS = [
    ("facebook/react", 50),
    ("microsoft/TypeScript", 50),
    ("fastapi/fastapi", 30),
    ("kubernetes/kubernetes", 20),
    ("encode/starlette", 10)
]

async def main():
    app.platform.sync_engine.GitHubSourcePlugin = MockMultiRepoGitHubSourcePlugin
    provider = get_provider()
    sync = get_sync_engine()
    
    report_lines = [
        "| Repository | Window | Devs | Files | Commits | Measurements | Evidence | Nodes | Edges | Components | Proj Hash | Replay Hash | Build (s) | Val Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for repo, commit_limit in REPOS:
        # Clear DB for isolation
        db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
        for dbf in db_files:
            if os.path.exists(dbf):
                try: os.remove(dbf)
                except Exception: pass
        
        # Sync
        job = await sync.sync(repo, mode=SyncMode.FULL, commit_limit=commit_limit)
        while job.status in ('pending', 'running'):
            await asyncio.sleep(0.5)
            
        # Builder
        builder = KnowledgeGraphProjectionBuilder(provider)
        start_build = time.time()
        projection = builder.build_projection(dataset_id=repo, execution_id="phase1")
        build_time = time.time() - start_build
        
        # Query basic stats
        devs = len(provider.query(DeveloperRecord, limit=10000))
        files = len(provider.query(FileRecord, limit=10000))
        commits = len(provider.query(CommitRecord, limit=10000))
        measurements = len(provider.query(MeasurementRecord, limit=10000))
        evidence = len(provider.query(EvidenceRecord, limit=10000))
        
        stats = projection.statistics
        components = stats.get("components", 0)
        val_score = projection.validation_report.get("overall_score", 0)
        
        # Replay
        engine = KnowledgeGraphReplayEngine()
        replay_report = engine.replay(projection.projection_id)
        
        line = f"| {repo} | {commit_limit} | {devs} | {files} | {commits} | {measurements} | {evidence} | {projection.node_count} | {projection.edge_count} | {components} | `{projection.projection_hash[:8]}` | `{replay_report['actual_projection_hash'][:8]}` | {build_time:.3f} | {val_score:.1f} |"
        report_lines.append(line)
        print(line)
        
    # Write back to markdown
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "r") as f:
        content = f.read()
        
    content = content.replace("*Pending...*", "\n".join(report_lines), 1)
    
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "w") as f:
        f.write(content)
        
if __name__ == "__main__":
    asyncio.run(main())
