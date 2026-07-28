from flask import Flask, render_template, request, jsonify
import datetime
import matplotlib.pyplot as plt
import os

# ==============================
# 🔹 INIT APP
# ==============================
app = Flask(__name__)

# ==============================
# 🔹 IN-MEMORY STORAGE
# ==============================
transactions = []

# ==============================
# 🔹 FRAUD LOGIC (RULE-BASED)
# ==============================
def calculate_fraud_score(data):
    score = 0
    reasons = []

    amount = data["amount"]
    location = data["location"]
    failed_attempts = data["failed_attempts"]
    hour = data["hour"]

    if amount > 50000:
        score += 35
        reasons.append("High transaction amount")

    if location.lower() not in ["salem", "chennai", "bangalore"]:
        score += 25
        reasons.append("Unusual location")

    if failed_attempts > 2:
        score += 20
        reasons.append("Multiple failed login attempts")

    if hour < 6 or hour > 23:
        score += 20
        reasons.append("Transaction at unusual time")

    if score >= 70:
        status = "FRAUD"
    elif score >= 40:
        status = "SUSPICIOUS"
    else:
        status = "GENUINE"

    return score, status, reasons


# ==============================
# 🔹 ALERT SYSTEM
# ==============================
def generate_alert(status):
    if status == "FRAUD":
        return "🚨 ALERT: Transaction Blocked! SMS & Email Sent."
    elif status == "SUSPICIOUS":
        return "⚠️ Warning: Suspicious Activity Detected."
    else:
        return "✅ Transaction Approved"


# ==============================
# 🔹 ROUTES
# ==============================

@app.route('/')
def home():
    return render_template('index.html')


# 🔹 ANALYZE (FORM + API SUPPORT)
@app.route('/analyze', methods=['POST'])
def analyze():

    # ======================
    # JSON REQUEST (React)
    # ======================
    if request.is_json:
        data_json = request.get_json()

        amount = float(data_json.get('amount', 0))
        failed_attempts = int(data_json.get('failed_attempts', 1))

        data = {
            "amount": amount,
            "location": "salem",
            "failed_attempts": failed_attempts,
            "hour": datetime.datetime.now().hour
        }

        score, status, reasons = calculate_fraud_score(data)

        return jsonify({
            "score": score,
            "status": status,
            "reasons": reasons
        })

    # ======================
    # FORM REQUEST (HTML)
    # ======================
    card = request.form['card']
    amount = float(request.form['amount'])
    location = request.form['location']
    merchant = request.form['merchant']
    failed_attempts = int(request.form['failed_attempts'])

    data = {
        "amount": amount,
        "location": location,
        "failed_attempts": failed_attempts,
        "hour": datetime.datetime.now().hour
    }

    score, status, reasons = calculate_fraud_score(data)
    alert = generate_alert(status)

    # Save transaction
    record = {
        "card": card[-4:],  # masked
        "amount": amount,
        "location": location,
        "status": status,
        "score": score
    }

    transactions.append(record)

    return render_template('result.html',
                           score=score,
                           status=status,
                           reasons=reasons,
                           alert=alert)


# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', data=transactions)


# 🔹 ANALYTICS GRAPH
@app.route('/analytics')
def analytics():
    fraud = sum(1 for t in transactions if t["status"] == "FRAUD")
    genuine = sum(1 for t in transactions if t["status"] == "GENUINE")

    labels = ['Fraud', 'Genuine']
    values = [fraud, genuine]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Fraud vs Genuine Transactions")

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig("static/chart.png")
    plt.close()

    return render_template("analytics.html")


# ==============================
# 🔹 RUN APP
# ==============================
if __name__ == '__main__':
    app.run(debug=True)