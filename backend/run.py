"""
HomeBrain - Backend & Root Application Launcher
"""
import sys
import os
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

for path in [BASE_DIR, PARENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    is_prod = bool(os.getenv("RENDER") or os.getenv("PORT"))

    # If running from inside backend directory:
    if os.path.exists("server.py"):
        app_module = "server:app"
    else:
        app_module = "backend.server:app"

    uvicorn.run(
        app_module,
        host=host,
        port=port,
        reload=not is_prod
    )

if __name__ == "__main__":
    main()
