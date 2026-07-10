import os
import sys
import subprocess
import json
import hashlib
import time
import platform
from datetime import datetime

# Orchestrator for Final Verification Sprint

PHASES = [
    ("Phase 1: End-to-End Repository Verification", "scripts/verification/phase1_e2e_repo.py"),
    ("Phase 2: Architectural Trace Audit", "scripts/verification/phase2_arch_trace.py"),
    ("Phase 3: Runtime Purity Audit", "scripts/verification/phase3_runtime_purity.py"),
    ("Phase 4: Projection Integrity Audit", "scripts/verification/phase4_projection_integrity.py"),
    ("Phase 5: API Contract Freeze", "scripts/verification/phase5_api_contract.py"),
    ("Phase 6A: Automated UI Contract Audit", "scripts/verification/phase6a_ui_contract.py"),
    ("Phase 7: Independent Production Gate", "scripts/verification/phase7_gate_generator.py")
]

ARTIFACTS = [
    "outputs/RepositoryValidation.json",
    "outputs/ArchitectureTraceAudit.md",
    "outputs/RuntimePurityAudit.md",
    "outputs/ProjectionIntegrityAudit.md",
    "outputs/ApiContract.json",
    "outputs/DeveloperConsoleAudit.json",
    "C:/Users/NITHIN/.gemini/antigravity-ide/brain/19a471b5-76a4-418f-b441-d6fb44f5cc9d/KnowledgeGraphProductionGate.md"
]

def hash_file(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def main():
    print("Starting Final Verification Sprint...\n")
    overall_status = "PASS"
    
    # Setup PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")
    
    for name, script_path in PHASES:
        print(f"Running {name} ({script_path})...")
        start_time = time.time()
        
        # We need to make sure the script exists
        if not os.path.exists(script_path):
            print(f"  [ERROR] Script {script_path} not found.")
            overall_status = "FAIL"
            break
            
        result = subprocess.run([sys.executable, script_path], env=env)
        
        duration = time.time() - start_time
        if result.returncode != 0:
            print(f"  [FAIL] {name} failed in {duration:.2f}s with exit code {result.returncode}")
            overall_status = "FAIL"
            break
        else:
            print(f"  [PASS] {name} completed in {duration:.2f}s")
            
    print("\nGenerating VerificationManifest.json...")
    
    manifest = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "git_commit": get_git_commit(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "datasets_tested": ["v1"],
        "repositories_tested": [
            "facebook/react",
            "microsoft/TypeScript",
            "fastapi/fastapi",
            "kubernetes/kubernetes",
            "encode/starlette"
        ],
        "generated_artifacts": {},
        "overall_verification_status": overall_status
    }
    
    for artifact in ARTIFACTS:
        h = hash_file(artifact)
        manifest["generated_artifacts"][os.path.basename(artifact)] = {
            "path": artifact,
            "sha256": h if h else "FILE_MISSING"
        }
        
    # Also include itself
    manifest_path = "outputs/VerificationManifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nVerification Sprint Finished. Status: {overall_status}")
    if overall_status == "PASS":
        print("\nAll gates passed. You may now tag the repository as kg-v1.0")
        
    sys.exit(0 if overall_status == "PASS" else 1)

if __name__ == "__main__":
    main()
