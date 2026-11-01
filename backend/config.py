import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")
FRONTEND_DIR = BASE_DIR.parent

# Vercel serverless environment handling:
# On Vercel, the application runs in a read-only filesystem, except /tmp.
if os.environ.get("VERCEL"):
    DATA_DIR = Path("/tmp/data")
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    ORIG_DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "hospitals.db"
    if not DB_PATH.exists() and (ORIG_DATA_DIR / "hospitals.db").exists():
        try:
            shutil.copy2(ORIG_DATA_DIR / "hospitals.db", DB_PATH)
        except Exception:
            pass
    JSON_EXPORT_PATH = DATA_DIR / "hospitals.json"
    if not JSON_EXPORT_PATH.exists() and (ORIG_DATA_DIR / "hospitals.json").exists():
        try:
            shutil.copy2(ORIG_DATA_DIR / "hospitals.json", JSON_EXPORT_PATH)
        except Exception:
            pass
    SECRET_KEY_PATH = DATA_DIR / "secret.key"
else:
    DATA_DIR = BASE_DIR / "data"
    try:
        DATA_DIR.mkdir(exist_ok=True)
    except OSError:
        pass
    DB_PATH = DATA_DIR / "hospitals.db"
    JSON_EXPORT_PATH = DATA_DIR / "hospitals.json"
    SECRET_KEY_PATH = DATA_DIR / "secret.key"

# Mapbox public tokens are delivered to the browser, so restrict them by URL in Mapbox.
DEFAULT_MAPBOX_KEY = os.environ.get("MAPBOX_ACCESS_TOKEN", "").strip()

DEFAULT_CENTER_LAT = 26.2183
DEFAULT_CENTER_LNG = 78.1828
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DEFAULT_ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
