from src.preprocessing import load_data, rename_columns, clean_data

print("Loading dataset...")

df = load_data("data/raw/ai4i2020.csv")

print("Dataset loaded ✔")
print(df.shape)

df = rename_columns(df)
df = clean_data(df)

print("Preprocessing OK ✔")
print(df.head())