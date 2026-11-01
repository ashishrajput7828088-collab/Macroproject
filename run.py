"""
Arogya Gwalior - Production Root Launcher
Enables 1-command startup from root: python run.py
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    from app import app
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"🏥 AROGYA GWALIOR ENTERPRISE MEDICAL SERVER ONLINE")
    print(f"👉 Public Portal: http://127.0.0.1:{port}")
    print(f"👉 Admin Portal:  http://127.0.0.1:{port}/admin")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=False)
