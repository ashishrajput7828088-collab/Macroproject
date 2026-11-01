import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
FRONTEND_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "hospitals.db"
JSON_EXPORT_PATH = DATA_DIR / "hospitals.json"
SECRET_KEY_PATH = DATA_DIR / "secret.key"

# Mapbox public tokens are delivered to the browser, so restrict them by URL in Mapbox.
DEFAULT_MAPBOX_KEY = os.environ.get("MAPBOX_ACCESS_TOKEN", "").strip()

DEFAULT_CENTER_LAT = 26.2183
DEFAULT_CENTER_LNG = 78.1828
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DEFAULT_ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
