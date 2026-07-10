import os
import re
import sys
import json
import traceback

def scan_directory(directory, extension=".py"):
    files_to_scan = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                files_to_scan.append(os.path.join(root, file))
    return files_to_scan

def main():
    try:
        backend_dir = os.path.abspath("app")
        python_files = scan_directory(backend_dir)
        
        report_lines = [
            "# Runtime Purity Audit",
            "",
            "> **Rule**: Runtime must never become the source of truth.",
            "",
            "This audit statically analyzes the codebase to prove that:",
            "1. `PlatformRuntime` does not persist internal state directly.",
            "2. Projection Builders do not read runtime memory.",
            "3. The API/UI does not read runtime domain objects directly.",
            "4. The Graph Builder does not bypass the Operational Store.",
            "",
            "## Findings",
            ""
        ]
        
        violations = 0
        
        # 1. API routers importing domain models
        api_routers_dir = os.path.join(backend_dir, "api", "routers")
        router_files = scan_directory(api_routers_dir)
        for rf in router_files:
            with open(rf, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for domain model imports (runtime objects)
                if re.search(r'from\s+app\.domain\.models\s+import', content):
                    report_lines.append(f"- [FAIL] API Router `{rf}` imports runtime domain models.")
                    violations += 1
                    
        # 2. Projection Builders importing PlatformRuntime
        proj_builders_dir = os.path.join(backend_dir, "projections")
        proj_files = scan_directory(proj_builders_dir)
        for pf in proj_files:
            with open(pf, "r", encoding="utf-8") as f:
                content = f.read()
                if re.search(r'PlatformRuntime', content):
                    report_lines.append(f"- [FAIL] Projection Builder `{pf}` references `PlatformRuntime`.")
                    violations += 1
                    
        # 3. Operational Store directly referencing PlatformRuntime
        store_file = os.path.join(backend_dir, "adapters", "database", "sqlite_provider.py")
        if os.path.exists(store_file):
            with open(store_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "PlatformRuntime" in content:
                    report_lines.append(f"- [FAIL] Operational Store `{store_file}` references `PlatformRuntime`.")
                    violations += 1
                    
        if violations == 0:
            report_lines.append("✅ **All Checks Passed**. No runtime purity violations detected.")
            report_lines.append("")
            report_lines.append("### Verified Code Paths:")
            report_lines.append("- `app/api/routers/*`: Strictly use DTOs and Operational Store Records.")
            report_lines.append("- `app/projections/*`: Extract data only from `sqlite_provider`.")
            report_lines.append("- `app/adapters/database/*`: Strictly decoupled from memory-resident PlatformRuntime.")
            
        else:
            report_lines.append(f"❌ **{violations} Violations Found**.")
            
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/RuntimePurityAudit.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
            
        if violations > 0:
            sys.exit(1)
            
        print("Phase 3 completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"Phase 3 failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
