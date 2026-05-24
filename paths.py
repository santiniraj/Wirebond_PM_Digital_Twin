from pathlib import Path

# =========================
# BASE DIRECTORY (CLOUD SAFE)
# =========================
BASE_DIR = Path(__file__).resolve().parent

# =========================
# MODELS
# =========================
MODEL_PATH = BASE_DIR / "model.pkl"
ENSEMBLE_MODEL_PATH = BASE_DIR / "ensemble_model.pkl"

# =========================
# DATA
# =========================
CLEANED_DATA_PATH = BASE_DIR / "cleaned_wirebond_data.csv"

# =========================
# FEATURES
# =========================
FEATURE_PATH = BASE_DIR / "features.json"

# =========================
# POWER BI OUTPUT
# =========================
POWERBI_PATH = BASE_DIR / "powerbi_master.csv"

# =========================
# LOGS
# =========================
LOG_DIR = BASE_DIR / "logs"
FEEDBACK_LOG_PATH = LOG_DIR / "feedback_log.csv"
PREDICTION_LOG_PATH = LOG_DIR / "prediction_history.csv"


# =========================
# VALIDATION (SAFE VERSION)
# =========================
def validate_paths():
    required = [
        MODEL_PATH,
        CLEANED_DATA_PATH,
        FEATURE_PATH
    ]

    missing = [str(p) for p in required if not p.exists()]

    if missing:
        raise FileNotFoundError(
            f"Missing required files: {missing}"
        )