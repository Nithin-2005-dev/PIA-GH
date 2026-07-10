import os
import sys
import json
import traceback
from fastapi.openapi.utils import get_openapi

def main():
    try:
        from app.api.server import app
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        
        # We can add stability status as a top-level extension or per-route
        openapi_schema["info"]["x-stability"] = "frozen"
        
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/ApiContract.json", "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2)
            
        print("Phase 5 completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"Phase 5 failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
