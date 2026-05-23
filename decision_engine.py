def maintenance_decision(prob):
    if prob < 0.3:
        return "LOW RISK", "No action required"
    elif prob < 0.7:
        return "MEDIUM RISK", "Schedule inspection"
    else:
        return "HIGH RISK", "Immediate maintenance required"