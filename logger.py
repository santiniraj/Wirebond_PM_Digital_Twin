import pandas as pd
import os
from datetime import datetime

LOG_FILE = "data/logs/prediction_history.csv"


def log_prediction(input_data, probability, risk):
    """
    Save every prediction for monitoring
    """

    os.makedirs("data/logs", exist_ok=True)

    row = input_data.copy()
    row["probability"] = probability
    row["risk"] = risk
    row["timestamp"] = datetime.now()

    df = pd.DataFrame([row])

    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)