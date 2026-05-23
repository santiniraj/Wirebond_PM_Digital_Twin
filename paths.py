import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "model.pkl")
ENSEMBLE_MODEL_PATH = os.path.join(BASE_DIR, "..", "ensemble_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "..", "cleaned_wirebond_data.csv")
FEATURE_PATH = os.path.join(BASE_DIR, "..", "features.json")