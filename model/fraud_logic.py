def calculate_fraud_score(data):
    score = 0
    reasons = []

    amount = data["amount"]
    location = data["location"]
    failed_attempts = data["failed_attempts"]
    hour = data["hour"]

    # 🔹 Rule 1: High amount
    if amount > 50000:
        score += 35
        reasons.append("High transaction amount")

    # 🔹 Rule 2: Location mismatch
    if location.lower() not in ["salem", "chennai", "bangalore"]:
        score += 25
        reasons.append("Unusual location")

    # 🔹 Rule 3: Failed attempts
    if failed_attempts > 2:
        score += 20
        reasons.append("Multiple failed login attempts")

    # 🔹 Rule 4: Time anomaly
    if hour < 6 or hour > 23:
        score += 20
        reasons.append("Transaction at unusual time")

    # 🔹 Decision
    if score >= 70:
        status = "FRAUD"
    elif score >= 40:
        status = "SUSPICIOUS"
    else:
        status = "GENUINE"

    return score, status, reasons