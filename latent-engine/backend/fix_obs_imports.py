import os
from pathlib import Path

replacements = {
    "app.observation.ingestion.sqlite_store": "app.observation.infrastructure.sqlite_store",
    "app.observation.ingestion.storage_manager": "app.observation.infrastructure.storage_manager"
}

def fix_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                for old, new in replacements.items():
                    new_content = new_content.replace(old, new)
                    
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {path}")

if __name__ == "__main__":
    fix_imports("C:/Users/NITHIN/Agentic_AI/latent-engine/backend/app")
