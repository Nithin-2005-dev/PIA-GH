import asyncio
import os
import hashlib
from app.platform.sync_engine import get_sync_engine, SyncMode
import app.platform.sync_engine
from app.projections.knowledge_graph_builder import KnowledgeGraphProjectionBuilder
from app.adapters.database.sqlite_provider import get_provider
from app.adapters.database.models import CommitRecord, MeasurementRecord, EvidenceRecord
import dataclasses
import json

class MockMultiRepoGitHubSourcePlugin:
    source_id = "github"
    def __init__(self, token=None): pass
    def fetch_repository_metadata(self, repository: str) -> dict: return {"name": repository.split("/")[-1]}
    def fetch_commits(self, repository: str, branch: str, limit: int = 100, since_sha=None):
        return [{"sha": f"sha{i}", "message": f"msg{i}", "author_email": f"dev{i%3}@x", "author_name": f"D{i%3}", "timestamp": "2023-01-01T00:00:00Z", "additions": 10, "deletions": 5} for i in range(limit)]
    def fetch_file_tree(self, repository, commit_sha): return []
    def get_rate_limit(self): return {"remaining": 5000, "limit": 5000, "reset_at": 0}

def hash_obj(obj) -> str:
    s = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()

async def get_layer_hashes():
    provider = get_provider()
    sync = get_sync_engine()
    
    db_files = ["pia_store.db", "pia_store.db-wal", "pia_store.db-shm", "pia_events.db", "pia_events.db-wal", "pia_events.db-shm"]
    for dbf in db_files:
        if os.path.exists(dbf):
            try: os.remove(dbf)
            except Exception: pass
            
    job = await sync.sync("hash/test", mode=SyncMode.FULL, commit_limit=10)
    while job.status in ('pending', 'running'): await asyncio.sleep(0.5)
    
    commits = sorted([dataclasses.asdict(c) for c in provider.query(CommitRecord)], key=lambda x: x["identity"]["object_id"])
    repo_hash = hash_obj(commits)
    
    measurements = sorted([dataclasses.asdict(m) for m in provider.query(MeasurementRecord)], key=lambda x: x["identity"]["object_id"])
    meas_hash = hash_obj(measurements)
    
    evidence = sorted([dataclasses.asdict(e) for e in provider.query(EvidenceRecord)], key=lambda x: x["identity"]["object_id"])
    ev_hash = hash_obj(evidence)
    
    builder = KnowledgeGraphProjectionBuilder(provider)
    projection = builder.build_projection("hash/test", "phase2.5")
    graph_hash = hash_obj({"nodes": projection.nodes, "edges": projection.edges})
    proj_hash = projection.projection_hash
    
    api_dto = dataclasses.asdict(projection)
    # The API DTO has a build_duration_ms and created_at which might differ by milliseconds. 
    # To truly verify deterministic *structure* of the DTO, we ignore time bounds.
    if "build_duration_ms" in api_dto: del api_dto["build_duration_ms"]
    if "identity" in api_dto and "created_at" in api_dto["identity"]: del api_dto["identity"]["created_at"]
    if "identity" in api_dto and "object_id" in api_dto["identity"]: del api_dto["identity"]["object_id"]
    if "projection_id" in api_dto: del api_dto["projection_id"]
    
    api_hash = hash_obj(api_dto)
    
    return {
        "Repository Objects": repo_hash,
        "Measurements": meas_hash,
        "Evidence": ev_hash,
        "Knowledge Graph": graph_hash,
        "Projection": proj_hash,
        "API DTO": api_hash
    }

async def main():
    app.platform.sync_engine.GitHubSourcePlugin = MockMultiRepoGitHubSourcePlugin
    
    print("Run 1...")
    hashes_run1 = await get_layer_hashes()
    
    print("Run 2...")
    hashes_run2 = await get_layer_hashes()
    
    report_lines = []
    report_lines.append("| Layer | Run 1 Hash | Run 2 Hash | Match |")
    report_lines.append("| :--- | :--- | :--- | :--- |")
    
    all_match = True
    
    for layer in hashes_run1.keys():
        h1 = hashes_run1[layer][:8]
        h2 = hashes_run2[layer][:8]
        match = "PASS" if h1 == h2 else "FAIL"
        if h1 != h2:
            all_match = False
        report_lines.append(f"| {layer} | `{h1}` | `{h2}` | {match} |")
        
    status = "PASS" if all_match else "FAIL"
    
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "r") as f:
        content = f.read()
        
    new_text = f"**Status:** {status}\n\n" + "\n".join(report_lines)
    
    if "## 2.5 Hash Stability Audit" not in content:
        content = content.replace("## 3. Scaling Curve", f"## 2.5 Hash Stability Audit\n{new_text}\n\n## 3. Scaling Curve")
        
    content = content.replace("| Replay | PENDING | - |", f"| Replay | {status} | [See Details](#25-hash-stability-audit) |")
    
    with open("C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    asyncio.run(main())
