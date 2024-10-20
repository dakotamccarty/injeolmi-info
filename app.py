import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = 'https://vidjdorjujsuhcaghquh.supabase.co'  # Replace with your Supabase URL
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpZGpkb3JqdWpzdWhjYWdocXVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk0MzAyNDIsImV4cCI6MjA0NTAwNjI0Mn0.sZZD9ifqfR3xQtYGs8GjkttS7D4W06Sih7R1uCl1SIw'  # Replace with your Supabase API Key
SUPABASE_TABLE = 'feeding_logs'  # The table you created for logs
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Function to log data (food, poop, pee, weight) into Supabase using requests
def log_entry(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, json=data, headers=SUPABASE_HEADERS)
    if response.status_code != 201:
        print(f"Error logging entry to {table}: {response.text}")

# Function to calculate the dog's age in months
def calculate_age_in_months(birthday):
    today = datetime.today()
    birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
    age_in_days = (today - birthday_date).days
    age_in_months = age_in_days / 30.44  # Average days in a month
    return age_in_months

# Function to calculate the food amount based on the dog's age in days
def calculate_food_amount(age_in_days):
    if age_in_days <= 60:
        return 288
    elif 60 < age_in_days <= 180:
        return 288 + ((age_in_days - 60) / (180 - 60)) * (507 - 288)
    elif 180 < age_in_days <= 240:
        return 507 + ((age_in_days - 180) / (240 - 180)) * (475 - 507)
    elif 240 < age_in_days <= 365:
        return 475 + ((age_in_days - 240) / (365 - 240)) * (323 - 475)
    else:
        return 323

# Function to get today's total food fed
def get_food_fed_today():
    url = f"{SUPABASE_URL}/rest/v1/feeding_logs?select=food_amount&timestamp=gte.{datetime.today().date()}"
    response = requests.get(url, headers=SUPABASE_HEADERS)
    if response.status_code == 200:
        feedings = response.json()
        return sum(entry['food_amount'] for entry in feedings)
    return 0

# Function to get today's poop and pee counts
def get_poop_pee_count():
    url = f"{SUPABASE_URL}/rest/v1/poop_log?select=poop_count,pee_count&timestamp=gte.{datetime.today().date()}"
    response = requests.get(url, headers=SUPABASE_HEADERS)
    if response.status_code == 200:
        logs = response.json()
        # Ensure None values are treated as 0
        poop_count = sum((log.get('poop_count') or 0) for log in logs)
        pee_count = sum((log.get('pee_count') or 0) for log in logs)
        return poop_count, pee_count
    return 0, 0

# Function to get the latest weight
def get_current_weight():
    url = f"{SUPABASE_URL}/rest/v1/weight?select=weight&order=timestamp.desc&limit=1"
    response = requests.get(url, headers=SUPABASE_HEADERS)
    if response.status_code == 200:
        result = response.json()
        if result:
            return result[0]['weight']
    return 0

# Set Injeolmi's birthday
injeolmi_birthday = "2024-06-27"

@app.route('/', methods=['GET', 'POST'])
def home():
    age_in_days = (datetime.today() - datetime.strptime(injeolmi_birthday, "%Y-%m-%d")).days
    age_in_months = calculate_age_in_months(injeolmi_birthday)
    recommended_grams_of_food = calculate_food_amount(age_in_days)
    
    # Get today's total food, poop, pee, and the current weight
    already_fed_today = get_food_fed_today()
    poop_count, pee_count = get_poop_pee_count()
    current_weight = get_current_weight()

    remaining_food = round(recommended_grams_of_food - already_fed_today, 2)

    if request.method == 'POST':
        # Handle food log input
        if 'food_amount' in request.form:
            food_amount = int(request.form['food_amount'])
            timestamp = datetime.now().isoformat()
            log_entry("feeding_logs", {"food_amount": food_amount, "timestamp": timestamp})
            return redirect(url_for('home'))

    return render_template("home.html", 
                           age_in_months=age_in_months, 
                           grams_of_food=remaining_food, 
                           already_fed_today=already_fed_today,
                           poop_count=poop_count, 
                           pee_count=pee_count,
                           current_weight=current_weight)

@app.route('/log-food', methods=['POST'])
def log_food():
    data = request.get_json()
    food_amount = data.get('food_amount')
    timestamp = data.get('timestamp')

    if not food_amount:
        return {"error": "Food amount is required"}, 400

    # Log the food entry
    log_entry("feeding_logs", {"food_amount": food_amount, "timestamp": timestamp})

    return {"success": True}, 200

# Log poop or pee using the same logic as food logging
@app.route('/log-poop-pee', methods=['POST'])
def log_poop_pee():
    data = request.get_json()
    log_type = data.get('type')
    timestamp = data.get('timestamp')

    if log_type not in ['poop', 'pee']:
        return jsonify({"error": "Invalid log type"}), 400

    entry = {"timestamp": timestamp}
    if log_type == "poop":
        entry["poop_count"] = 1
    else:
        entry["pee_count"] = 1

    log_entry("poop_log", entry)
    
    return jsonify({"success": True}), 200

# Log weight changes using the same logic as food logging
@app.route('/log-weight', methods=['POST'])
def log_weight():
    data = request.get_json()
    weight = data.get('weight')
    timestamp = data.get('timestamp')

    log_entry("weight", {"weight": weight, "timestamp": timestamp})

    return jsonify({"success": True}), 200

if __name__ == "__main__":
    app.run(debug=True)