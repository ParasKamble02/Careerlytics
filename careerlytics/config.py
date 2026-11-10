import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_PATH = ROOT / "models" / "match_model.joblib"
SQLITE_PATH = DATA_DIR / "careerlytics.db"

DB_URL = os.getenv("CAREERLYTICS_DB_URL", "").strip()

APP_NAME = "Careerlytics"
TAGLINE = "AI-Powered Career Intelligence and Job Recommendation Platform"

SEED_JOBS = 1240
RANDOM_SEED = 42

# Final recommendation score = weighted blend of these (sums to 1.0)
SCORE_WEIGHTS = {"ml": 0.45, "skill": 0.20, "role": 0.10, "location": 0.10, "experience": 0.10, "text": 0.05}
TIERS = (("Strong", 0.75), ("Good", 0.60), ("Stretch", 0.0))
