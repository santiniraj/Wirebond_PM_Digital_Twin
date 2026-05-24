import numpy as np

def create_features(df):

    # temperature difference
    df["Temperature_Difference"] = (
        df["Heater_Block_Temperature"] - df["Bond_Head_Temperature"]
    )

    # safe ratio
    df["Force_Speed_Ratio"] = (
        df["Bonding_Force"] / (df["Bonding_Speed"] + 1e-6)
    )

    # stress index
    df["Stress_Index"] = (
        df["Bonding_Force"] * df["Bonding_Speed"]
    )

    # wear interaction
    df["Wear_Temp_Interaction"] = (
        df["Capillary_Wear"] * df["Temperature_Difference"]
    )

    return df