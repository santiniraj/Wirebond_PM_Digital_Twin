import json
import os
from datetime import datetime

LOG_FILE = os.path.join("data", "feedback_log.json")


def save_feedback(input_data, prediction, probability, feedback, machine_id=None):

    record = {
        "timestamp": datetime.now().isoformat(),
        "machine_id": machine_id,
        "input": input_data,
        "prediction": prediction,
        "probability": float(probability),
        "feedback": feedback
    }

    # initialize file safely
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    # read safely
    with open(LOG_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # append
    data.append(record)

    # write back
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)