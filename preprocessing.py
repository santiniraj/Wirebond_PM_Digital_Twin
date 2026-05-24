import pandas as pd

MACHINE_MAP = {
    0: "WBO001",
    1: "WBO002",
    2: "WBO003"
}

def load_data(path):
    return pd.read_csv(path)


def rename_columns(df):
    return df.rename(columns={
        "Air temperature [K]": "Bond_Head_Temperature",
        "Process temperature [K]": "Heater_Block_Temperature",
        "Rotational speed [rpm]": "Bonding_Speed",
        "Torque [Nm]": "Bonding_Force",
        "Tool wear [min]": "Capillary_Wear",
        "Machine failure": "Wirebond_Failure"
    })


def clean_data(df):

    df = df.drop(columns=["UDI", "Product ID"], errors="ignore")

    # SAFE TYPE HANDLING (NO NaN cascade)
    if df["Type"].dtype == "object":
        df["Type"] = df["Type"].replace({
            "L": 0,
            "M": 1,
            "H": 2
        })

    df["Type"] = pd.to_numeric(df["Type"], errors="coerce")

    return df


def add_machine_column(df):

    df["Machine"] = df["Type"].map(MACHINE_MAP)

    # SAFETY FIX (prevents NaN machines)
    df["Machine"] = df["Machine"].fillna("WBO001")

    return df