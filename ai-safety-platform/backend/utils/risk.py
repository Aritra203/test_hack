def classify_risk(toxicity_score: float) -> str:
    if toxicity_score > 0.8:
        return "HIGH"
    if toxicity_score > 0.5:
        return "MEDIUM"
    return "LOW"
