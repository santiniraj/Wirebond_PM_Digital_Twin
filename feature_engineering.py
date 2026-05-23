import pandas as pd

def create_features(df):

    df["Temperature_Difference"] = (
        df["Heater_Block_Temperature"] - df["Bond_Head_Temperature"]
    )

    df["Force_Speed_Ratio"] = (
        df["Bonding_Force"] / df["Bonding_Speed"]
    )

    df["Stress_Index"] = (
        df["Bonding_Force"] * df["Bonding_Speed"]
    )

    df["Wear_Interaction"] = (
        df["Capillary_Wear"] * df["Temperature_Difference"]
    )

    return df