import uuid
import sys
import asyncio
from collections import Counter
from app.platform.sync_engine import get_sync_engine, SyncMode
from app.adapters.database.sqlite_provider import get_provider
from app.adapters.database.models import MeasurementRecord, EvidenceRecord, ExecutionRecord, GlobalIdentity

async def main():
    provider = get_provider()
    sync = get_sync_engine()

    latest_exec = provider.query(ExecutionRecord, limit=1)[0]
    m_records_1 = {m.object_id: m for m in provider.query(MeasurementRecord, limit=1000) if m.identity.execution_id == latest_exec.object_id}
    e_records_1 = {e.object_id: e for e in provider.query(EvidenceRecord, limit=1000) if e.identity.execution_id == latest_exec.object_id}

    print(f'Original Measurements: {len(m_records_1)}')
    print(f'Original Evidence: {len(e_records_1)}')

    for m_id in m_records_1.keys():
        provider.delete(MeasurementRecord, m_id)
    for e_id in e_records_1.keys():
        provider.delete(EvidenceRecord, e_id)
    print('Measurements and Evidence deleted.')

    job = await sync.sync('facebook/react', mode=SyncMode.FULL, commit_limit=30, github_token="x")
    while job.status in ('pending', 'running'):
        await asyncio.sleep(1)
    print(f'Sync finished with status: {job.status}')

    new_exec = provider.query(ExecutionRecord, limit=1)[0]
    m_records_2 = {m.object_id: m for m in provider.query(MeasurementRecord, limit=1000) if m.identity.execution_id == new_exec.object_id}
    e_records_2 = {e.object_id: e for e in provider.query(EvidenceRecord, limit=1000) if e.identity.execution_id == new_exec.object_id}
    print(f'Regenerated Measurements: {len(m_records_2)}')
    print(f'Regenerated Evidence: {len(e_records_2)}')

    m_diff = set(m_records_1.keys()) ^ set(m_records_2.keys())
    e_diff = set(e_records_1.keys()) ^ set(e_records_2.keys())
    print(f'Measurement ID Diffs: {len(m_diff)}')
    print(f'Evidence ID Diffs: {len(e_diff)}')

if __name__ == '__main__':
    asyncio.run(main())
