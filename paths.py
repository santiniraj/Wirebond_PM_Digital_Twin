from pathlib import Path

# =========================
# ROOT DIRECTORY (Streamlit-safe)
# =========================
ROOT_DIR = Path(__file__).resolve().parent

# =========================
# MODEL PATHS
# =========================
MODEL_PATH = ROOT_DIR / "model.pkl"
FEATURE_PATH = ROOT_DIR / "features.json"
ENSEMBLE_MODEL_PATH = ROOT_DIR / "ensemble_model.pkl"

# =========================
# DATA PATHS
# =========================
DATA_PATH = ROOT_DIR / "cleaned_wirebond_data.csv"

# =========================
# POWER BI EXPORT
# =========================
POWERBI_PATH = ROOT_DIR / "powerbi_feed.csv"