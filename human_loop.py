import json
import os

LOG_FILE = os.path.join("data", "feedback_log.json")


def save_feedback(input_data, prediction, probability, feedback):
    record = {
        "input": input_data,
        "prediction": prediction,
        "probability": probability,
        "feedback": feedback
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    data.append(record)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)