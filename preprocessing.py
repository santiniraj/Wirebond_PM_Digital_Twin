import pandas as pd

def load_data(path):
    return pd.read_csv(path)


def rename_columns(df):
    df = df.rename(columns={
        "Air temperature [K]": "Bond_Head_Temperature",
        "Process temperature [K]": "Heater_Block_Temperature",
        "Rotational speed [rpm]": "Bonding_Speed",
        "Torque [Nm]": "Bonding_Force",
        "Tool wear [min]": "Capillary_Wear",
        "Machine failure": "Wirebond_Failure"
    })
    return df


def clean_data(df):
    df = df.drop(columns=["UDI", "Product ID"], errors="ignore")
    df["Type"] = df["Type"].map({"L": 0, "M": 1, "H": 2})
    return df