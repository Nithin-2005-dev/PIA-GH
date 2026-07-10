import os
import sys
import traceback
import asyncio

from app.adapters.database.sqlite_provider import get_provider
from app.adapters.database.models import KnowledgeGraphProjectionRecord
from app.projections.graph_replay import KnowledgeGraphReplayEngine

def main():
    try:
        provider = get_provider()
        
        projections = provider.query(KnowledgeGraphProjectionRecord, limit=100)
        
        if not projections:
            print("No projections found in Operational Store. Run Phase 1 first.")
            sys.exit(1)
            
        report_lines = [
            "# Projection Integrity Audit",
            "",
            "This audit validates the integrity of all persisted projections in the Operational Store.",
            ""
        ]
        
        engine = KnowledgeGraphReplayEngine()
        
        overall_pass = True
        
        for p in projections:
            pid = p.projection_id
            
            report_lines.append(f"## Projection: `{pid}`")
            
            checks = []
            
            # 1. Builder version recorded
            if getattr(p, 'builder_version', None):
                checks.append("- [x] Builder version recorded")
            else:
                checks.append("- [ ] Builder version recorded")
                overall_pass = False
                
            # 2. Schema version recorded
            if getattr(p, 'schema_version', None):
                checks.append("- [x] Schema version recorded")
            else:
                checks.append("- [ ] Schema version recorded")
                overall_pass = False
                
            # 3. Dataset recorded (Check identity)
            if getattr(p.identity, 'dataset_id', None) or getattr(p, 'dataset_id', None):
                checks.append("- [x] Dataset recorded")
            else:
                checks.append("- [ ] Dataset recorded")
                overall_pass = False
                
            # 4. Execution recorded (Check identity)
            if getattr(p.identity, 'execution_id', None) or getattr(p, 'execution_id', None):
                checks.append("- [x] Execution recorded")
            else:
                checks.append("- [ ] Execution recorded")
                overall_pass = False
                
            # 5. Validation report linked
            if getattr(p, 'validation_report', None):
                checks.append("- [x] Validation report linked")
            else:
                checks.append("- [ ] Validation report linked")
                overall_pass = False
                
            # 6. Provenance complete (check nodes and edges for provenance fields)
            provenance_ok = True
            for node in getattr(p, 'nodes', []):
                if not node.get('attributes', {}).get('provenance'):
                    provenance_ok = False
                    break
            if provenance_ok:
                for edge in getattr(p, 'edges', []):
                    if not edge.get('provenance'):
                        provenance_ok = False
                        break
                        
            if provenance_ok:
                checks.append("- [x] Provenance complete")
            else:
                checks.append("- [ ] Provenance complete")
                overall_pass = False
                
            # 7. Hash matches serialized content (Replay Engine does this)
            # Replay hash matches
            try:
                replay = engine.replay(pid)
                if replay.get('match', False):
                    checks.append(f"- [x] Replay hash matches (`{replay['actual_projection_hash'][:8]}`)")
                else:
                    checks.append(f"- [ ] Replay hash matches (Expected: {replay.get('expected_projection_hash')}, Actual: {replay.get('actual_projection_hash')})")
                    overall_pass = False
            except Exception as e:
                checks.append(f"- [ ] Replay engine failed: {e}")
                overall_pass = False
                
            report_lines.extend(checks)
            report_lines.append("")
            
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/ProjectionIntegrityAudit.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
            
        if not overall_pass:
            print("Phase 4 failed: One or more integrity checks failed.")
            sys.exit(1)
            
        print("Phase 4 completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"Phase 4 failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
