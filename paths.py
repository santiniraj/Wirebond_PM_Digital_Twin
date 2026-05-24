from pathlib import Path

# =========================
# ROOT (Streamlit Cloud safe)
# =========================
ROOT_DIR = Path(__file__).resolve().parent

# =========================
# MODEL + FEATURES
# =========================
MODEL_PATH = ROOT_DIR / "model.pkl"
FEATURE_PATH = ROOT_DIR / "features.json"
ENSEMBLE_MODEL_PATH = ROOT_DIR / "ensemble_model.pkl"

# =========================
# DATA
# =========================
DATA_PATH = ROOT_DIR / "cleaned_wirebond_data.csv"

# =========================
# OUTPUT
# =========================
POWERBI_PATH = ROOT_DIR / "powerbi_feed.csv"