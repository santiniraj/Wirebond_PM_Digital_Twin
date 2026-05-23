from src.preprocessing import load_data, rename_columns, clean_data
from src.feature_engineering import create_features

print("Loading data...")

df = load_data("data/raw/ai4i2020.csv")

df = rename_columns(df)
df = clean_data(df)

print("Applying feature engineering...")

df = create_features(df)

print("Feature engineering SUCCESS ✔")

print(df.head())

print("\nNew columns:")
print(df.columns)