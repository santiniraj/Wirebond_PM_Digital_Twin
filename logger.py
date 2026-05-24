import pandas as pd
import os
from datetime import datetime

LOG_FILE = "data/logs/prediction_history.csv"


def log_prediction(input_data, probability, risk, machine_id=None):

    os.makedirs("data/logs", exist_ok=True)

    row = input_data.copy()

    # enforce SCADA traceability
    row["machine_id"] = machine_id

    row["probability"] = float(probability)
    row["risk"] = risk

    # stable timestamp format (Power BI friendly)
    row["timestamp"] = datetime.now().isoformat()

    df = pd.DataFrame([row])

    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)