from pathlib import Path

# =========================
# BASE DIRECTORY (CLOUD SAFE)
# =========================
BASE_DIR = Path(__file__).resolve().parent

# =========================
# MODEL
# =========================
MODEL_PATH = BASE_DIR / "model.pkl"
FEATURE_PATH = BASE_DIR / "features.json"

# =========================
# DATA
# =========================
CLEANED_DATA_PATH = BASE_DIR / "cleaned_wirebond_data.csv"

# =========================
# POWER BI OUTPUT
# =========================
POWERBI_PATH = BASE_DIR / "powerbi_feed.csv"