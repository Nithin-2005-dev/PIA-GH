import asyncio
import time
from app.platform.sync_engine import get_sync_engine, SyncMode

async def main():
    e = get_sync_engine()
    print("Starting sync...")
    j = await e.sync('facebook/react', mode=SyncMode.FULL, commit_limit=30, github_token="x")
    print('Sync started', j.job_id)
    
    while j.status in ('pending', 'running'):
        await asyncio.sleep(1)
        print('Status:', j.status, j.current_operation, j.commits_processed)
        
    print('Done:', j.status)
    if hasattr(j, 'error'):
        print('Error:', j.error)

asyncio.run(main())
