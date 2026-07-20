import re
import os
import sys
from pathlib import Path

def update_metrics():
    backend_dir = Path(__file__).parent.parent.parent
    
    # We will search for all files that register rules or define them.
    # To be extremely accurate, we could just grep for `class .*Rule[ \(:]`
    rule_names = set()
    
    for py_file in backend_dir.rglob('*.py'):
        if 'tests' in str(py_file) or py_file.is_dir():
            continue
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        
        # Match class definitions for Rules
        matches = re.findall(r'class ([A-Za-z0-9]+Rule)[\(:]', content)
        for m in matches:
            if m not in ('ReasoningRule', 'CausalRule'):
                rule_names.add(m)

    rule_count = len(rule_names)
    
    md_path = Path(r"C:\Users\NITHIN\.gemini\antigravity-ide\brain\19a471b5-76a4-418f-b441-d6fb44f5cc9d\migration_map.md")
    
    if not md_path.exists():
        print(f"Cannot find {md_path}")
        return
        
    md_content = md_path.read_text(encoding='utf-8')
    
    new_table = f"""| Metric | Count |
| :--- | :--- |
| Rules discovered | {rule_count} |
| Rules migrated | 0 |
| Rules validated | 0 |
| Rules deprecated | 0 |
| Rules remaining | {rule_count} |"""

    updated_md = re.sub(r'\| Metric \| Count \|.*?\| Rules remaining \| \d+ \|', new_table, md_content, flags=re.DOTALL)
    
    md_path.write_text(updated_md, encoding='utf-8')
    print(f"Updated metrics: Discovered {rule_count} rules. Names: {', '.join(list(rule_names)[:5])}...")

if __name__ == "__main__":
    update_metrics()
