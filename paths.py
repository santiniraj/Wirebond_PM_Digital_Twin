from pathlib import Path

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = Path(__file__).resolve().parent

# =========================
# FILE PATHS (STREAMLIT SAFE)
# =========================
MODEL_PATH = BASE_DIR / "model.pkl"
FEATURE_PATH = BASE_DIR / "features.json"
CLEANED_DATA_PATH = BASE_DIR / "cleaned_wirebond_data.csv"