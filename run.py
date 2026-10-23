"""
HomeBrain - Root Application Launcher
Starts the FastAPI REST API Server & Web Dashboard on http://localhost:8000
Amazon Developer Hackathon 2026 | Alexa+ Track
"""

import sys
import os
import uvicorn

# Ensure backend is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

def main():
    print("\n" + "=" * 76)
    print("  HOMEBRAIN -- Goal-Driven Smart Home Agent Protocol for Alexa+")
    print("  Amazon Developer Hackathon 2026 | Alexa+ Track")
    print("=" * 76)
    print("  [+] Web Dashboard       : http://localhost:8000")
    print("  [+] Interactive API Docs : http://localhost:8000/docs")
    print("  [+] 12 MCP Tools JSON   : http://localhost:8000/api/mcp/tools")
    print("  [+] Terminal Demo Run   : python run_demo.py")
    print("=" * 76 + "\n")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    is_prod = bool(os.getenv("RENDER") or os.getenv("PORT"))

    uvicorn.run(
        "backend.server:app",
        host=host,
        port=port,
        reload=not is_prod
    )

if __name__ == "__main__":
    main()
