import asyncio
import os
import time
from app.platform.sync_engine import get_sync_engine, SyncMode
import app.platform.sync_engine
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder
from app.projections.graph_replay import KnowledgeGraphReplayEngine
from app.adapters.database.sqlite_provider import get_provider

class MockMultiRepoGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None):
        pass
    def fetch_repository_metadata(self, repository: str) -> dict: return {"name": repository.split("/")[-1]}
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
    def fetch_file_tree(self, repository, commit_sha): return []
    def get_rate_limit(self): return {"remaining": 5000, "limit": 5000, "reset_at": 0}

async def main():
    app.platform.sync_engine.GitHubSourcePlugin = MockMultiRepoGitHubSourcePlugin
    provider = get_provider()
    sync = get_sync_engine()
    
    first_run_state = None
    pass_all = True
    
    report_lines = []
    
    for i in range(1, 11):
        print(f"Run {i}/10...")
        
        # Clear DB to force full re-evaluation
        db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
        for dbf in db_files:
            if os.path.exists(dbf):
                try: os.remove(dbf)
                except Exception: pass
                
        # Sync
        job = await sync.sync("facebook/react", mode=SyncMode.FULL, commit_limit=50)
        while job.status in ('pending', 'running'):
            await asyncio.sleep(0.5)
            
        # Build
        builder = KnowledgeGraphProjectionBuilder(provider)
        projection = builder.build_projection(dataset_id="facebook/react", execution_id=f"phase2_run_{i}")
        
        # Replay
        engine = KnowledgeGraphReplayEngine()
        replay_report = engine.replay(projection.projection_id)
        
        # Collect State
        node_ids = sorted([n['id'] for n in projection.nodes])
        edge_signatures = sorted([f"{e['source']}->{e['target']}" for e in projection.edges])
        
        state = {
            "projection_hash": projection.projection_hash,
            "replay_hash": replay_report["actual_projection_hash"],
            "node_count": projection.node_count,
            "edge_count": projection.edge_count,
            "validation_score": projection.validation_report.get("overall_score"),
            "node_ids": node_ids,
            "edge_signatures": edge_signatures
        }
        
        if i == 1:
            first_run_state = state
            report_lines.append(f"- Run 1: Hash `{state['projection_hash'][:12]}` | Nodes {state['node_count']} | Edges {state['edge_count']} | Score {state['validation_score']}")
        else:
            diffs = []
            for k in state:
                if state[k] != first_run_state[k]:
                    if k in ['node_ids', 'edge_signatures']:
                        diffs.append(f"Mismatch in {k}")
                    else:
                        diffs.append(f"{k}: {first_run_state[k]} != {state[k]}")
                        
            if not diffs:
                report_lines.append(f"- Run {i}: IDENTICAL")
            else:
                pass_all = False
                report_lines.append(f"- Run {i}: FAILED -> {', '.join(diffs)}")
                
    result = "PASS" if pass_all else "FAIL"
    
    # Write back to markdown
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "r") as f:
        content = f.read()
        
    new_text = f"**Status:** {result}\n\n" + "\n".join(report_lines)
    content = content.replace("## 2. Determinism & Hash Stability\n*Pending...*", f"## 2. Determinism & Hash Stability\n{new_text}", 1)
    
    content = content.replace("| Determinism | PENDING | - |", f"| Determinism | {result} | [See Details](#2-determinism--hash-stability) |")
    
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    asyncio.run(main())
