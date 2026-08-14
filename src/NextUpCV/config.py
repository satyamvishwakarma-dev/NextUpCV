import os
from pathlib import Path

# Base & Data Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database & Application Constants
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "NextUpCV.db"))
SPACY_MODEL = "en_core_web_sm"
MAX_FILE_SIZE_MB = 5
