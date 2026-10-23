"""
HomeBrain - Entry Point when Render Root Directory is set to frontend
Amazon Developer Hackathon 2026 | Alexa+ Track
"""
import sys
import os
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

for p in [PROJECT_ROOT, BACKEND_DIR, CURRENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    try:
        from backend.server import app
    except ImportError:
        from server import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False
    )

if __name__ == "__main__":
    main()
