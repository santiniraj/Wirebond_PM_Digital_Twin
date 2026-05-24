import pandas as pd
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier

from src.preprocessing import load_data, rename_columns, clean_data
from src.feature_engineering import create_features
from src.paths import CLEANED_DATA_PATH, MODEL_PATH, FEATURE_PATH


# =========================
# LOAD DATA
# =========================
df = load_data(CLEANED_DATA_PATH)
df = rename_columns(df)
df = clean_data(df)
df = create_features(df)

# =========================
# REMOVE LEAKAGE FEATURES
# =========================
leak_cols = ["HDF", "OSF", "RNF", "TWF", "PWF"]
df = df.drop(columns=leak_cols, errors="ignore")

# =========================
# FEATURES & TARGET
# =========================
X = df.drop("Wirebond_Failure", axis=1)
y = df["Wirebond_Failure"]

# =========================
# TRAIN / TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

# =========================
# PREPROCESS PIPELINE
# =========================
preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), X.columns)
])

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

pipeline = Pipeline([
    ("preprocess", preprocess),
    ("model", model)
])

# =========================
# TRAIN
# =========================
pipeline.fit(X_train, y_train)

# =========================
# SAVE MODEL
# =========================
joblib.dump(pipeline, MODEL_PATH)

# =========================
# SAVE FEATURES (CRITICAL FOR DASHBOARD CONSISTENCY)
# =========================
with open(FEATURE_PATH, "w") as f:
    json.dump(list(X.columns), f)

print("✔ Model trained successfully")