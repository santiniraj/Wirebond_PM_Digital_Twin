import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = os.path.join(BASE_DIR, "data/processed/cleaned_wirebond_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models/trained/model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "models/trained/features.json")