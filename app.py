from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

expenses = {}
next_id = 1

@app.route("/api/expenses/summary", methods=["GET"])
def get_summary():
    month = request.args.get("month")
    
    mapping = {
        "1": "January",
        "2": "February",
        "3": "March",
        "4": "April",
        "5": "May",
        "6": "June",
        "7": "July",
        "8": "August",
        "9": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    if month:
        if int(month) < 1 or int(month) > 12:
            return jsonify({"error": "Please enter a valid month between 1 and 12"}), 400

        total = 0
        for id in expenses:
            expense_date = datetime.strptime(expenses[id]["date"], "%m-%d-%Y")
            if expense_date.month == int(month):
                total += float(expenses[id]["amount"])

        return jsonify({
            "month": mapping[month],
            "total": total
        }), 200

    total = sum(expenses[id]["amount"] for id in expenses)
    
    return jsonify({"message": f"Total amount of expenses: ${total}"}), 200

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    if expense_id not in expenses:
        return jsonify({"error": "expense_id not in expenses"}), 404

    del expenses[expense_id]
    return "", 204

@app.route("/api/expenses/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    if expense_id not in expenses:
        return jsonify({"error": "expense_id not in expenses"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    allowed_fields = ["description", "amount"]
    for field in allowed_fields:
        if field in data:
            expenses[expense_id][field] = data[field]
    
    return jsonify(expenses[expense_id]), 200
    

@app.route("/api/expenses", methods=["GET"])
def view_expenses():
    return jsonify(expenses), 200

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    if expense_id not in expenses:
        return jsonify({"error": "ID not found in expenses"}), 404
    return jsonify(expenses[expense_id]), 200

@app.route("/api/expenses", methods=["POST"])
def create_expense():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "description" not in data or "amount" not in data:
        return jsonify({"error": "description and amount of the expense are both required."}), 400  # 400 BAD REQUEST
    
    # Validate amount is a positive number
    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    global next_id
    today = datetime.now().strftime("%m-%d-%Y")  # Extract only the date

    expense = {
        "id": next_id,
        "date": today,
        "description": data["description"],
        "amount": amount
    }

    expenses[next_id] = expense
    next_id += 1
    return jsonify(expense), 201

if __name__ == "__main__":
    app.run(debug=True)