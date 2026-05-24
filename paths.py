import os

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path(*paths):
    """Helper to build OS-safe paths"""
    return os.path.join(BASE_DIR, *paths)


# =========================
# MODELS
# =========================
MODEL_PATH = get_path("..", "models", "trained", "model.pkl")
ENSEMBLE_MODEL_PATH = get_path("..", "models", "trained", "ensemble_model.pkl")

# =========================
# DATA (SINGLE SOURCE OF TRUTH)
# =========================
RAW_DATA_PATH = get_path("..", "data", "raw")
PROCESSED_DATA_PATH = get_path("..", "data", "processed")
CLEANED_DATA_PATH = get_path("..", "data", "processed", "cleaned_wirebond_data.csv")

# =========================
# POWER BI OUTPUT
# =========================
POWERBI_PATH = get_path("..", "powerbi_master.csv")

# =========================
# FEATURES
# =========================
FEATURE_PATH = get_path("..", "models", "trained", "features.json")

# =========================
# LOGS
# =========================
LOG_DIR = get_path("..", "data", "logs")
FEEDBACK_LOG_PATH = get_path("..", "data", "logs", "feedback_log.csv")
PREDICTION_LOG_PATH = get_path("..", "data", "logs", "prediction_history.csv")


# =========================
# SAFETY CHECK (optional but recommended)
# =========================
def validate_paths():
    required_paths = [
        MODEL_PATH,
        CLEANED_DATA_PATH,
        FEATURE_PATH
    ]

    missing = [p for p in required_paths if not os.path.exists(p)]

    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")