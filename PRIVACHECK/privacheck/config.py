from pathlib import Path
APP_NAME = "PRIVACHECK AI"
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"
DB_PATH = DATA_DIR / "privacheck.db"
for folder in (DATA_DIR, UPLOAD_DIR, REPORT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT_DIR / "models"
DATASET_DIR = ROOT_DIR / "datasets"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)
