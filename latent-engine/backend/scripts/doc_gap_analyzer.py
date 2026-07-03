import os
import ast
import glob
from pathlib import Path

def analyze_file(filepath):
    gaps = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        # Check module docstring
        module_doc = ast.get_docstring(tree)
        if not module_doc:
            gaps.append("- [ ] Module-level docstring is missing.")
        else:
            doc_lower = module_doc.lower()
            if "purpose" not in doc_lower:
                gaps.append("- [ ] Module docstring missing 'Purpose'.")
            if "dependencies" not in doc_lower and "inputs" not in doc_lower:
                gaps.append("- [ ] Module docstring might be missing 'Inputs/Outputs/Dependencies'.")
                
        # Check classes
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        for cls in classes:
            cls_doc = ast.get_docstring(cls)
            if not cls_doc:
                gaps.append(f"- [ ] Class `{cls.name}` docstring is missing.")
            else:
                doc_lower = cls_doc.lower()
                if "responsibilities" not in doc_lower and "why it exists" not in doc_lower:
                    gaps.append(f"- [ ] Class `{cls.name}` docstring missing rationale/responsibilities.")

        # Check functions
        functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for func in functions:
            if func.name.startswith('_') and func.name != "__init__":
                continue # Skip private methods for now to reduce noise, though they might need docs too
            func_doc = ast.get_docstring(func)
            if not func_doc:
                gaps.append(f"- [ ] Function `{func.name}` docstring is missing.")
                
    except Exception as e:
        gaps.append(f"- [ ] Error parsing file: {e}")
        
    return gaps

def main():
    repo_root = Path(r"c:\Users\NITHIN\Agentic_AI\latent-engine")
    backend_dir = repo_root / "backend"
    docs_dir = repo_root / "docs"
    
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
        
    report_path = docs_dir / "documentation_gap_report.md"
    
    all_py_files = list(backend_dir.rglob("*.py"))
    
    report_content = [
        "# Documentation Gap Report\n",
        "This report is automatically generated based on the Zero Knowledge Loss Policy.\n"
    ]
    
    total_files = len(all_py_files)
    fully_documented = 0
    
    for py_file in sorted(all_py_files):
        # Skip standard venv or hidden folders if they exist
        if ".venv" in py_file.parts or ".git" in py_file.parts:
            continue
            
        gaps = analyze_file(py_file)
        rel_path = py_file.relative_to(repo_root)
        
        if not gaps:
            fully_documented += 1
            report_content.append(f"## {rel_path}\n- Status: **Fully Documented** :white_check_mark:\n")
        else:
            report_content.append(f"## {rel_path}\n- Status: **Missing Documentation** :x:\n")
            report_content.extend(gaps)
            report_content.append("\n")
            
    report_content.insert(2, f"**Summary**: {fully_documented}/{total_files} files fully documented.\n\n")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
        
    print(f"Documentation gap report generated at: {report_path}")

if __name__ == "__main__":
    main()
