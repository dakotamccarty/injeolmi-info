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

# Function to log food data into Supabase using requests
def log_food_entry(food_amount, timestamp):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    data = {
        "food_amount": food_amount,
        "timestamp": timestamp
    }

    response = requests.post(url, json=data, headers=SUPABASE_HEADERS)

    # Log the response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    # If the request is successful, just return None
    if response.status_code == 201:
        return None  # No need to process any response
    else:
        print(f"Error logging data: {response.text}")
        return {"error": f"Supabase API returned error {response.status_code}"}

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

# Function to get total food fed today from Supabase
def get_food_fed_today():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=food_amount&timestamp=gte.{datetime.today().date()}"
    response = requests.get(url, headers=SUPABASE_HEADERS)
    if response.status_code == 200:
        feedings = response.json()
        total_fed_today = sum(entry['food_amount'] for entry in feedings)
        return total_fed_today
    else:
        return 0

# Set Injeolmi's birthday
injeolmi_birthday = "2024-07-01"

@app.route('/', methods=['GET', 'POST'])
def home():
    # Calculate age in days and months
    age_in_days = (datetime.today() - datetime.strptime(injeolmi_birthday, "%Y-%m-%d")).days
    age_in_months = calculate_age_in_months(injeolmi_birthday)
    recommended_grams_of_food = calculate_food_amount(age_in_days)
    
    # Get today's total food already fed
    already_fed_today = get_food_fed_today()
    
    # Calculate the remaining food, rounding to 2 decimal places
    remaining_food = round(recommended_grams_of_food - already_fed_today, 2)

    if request.method == 'POST':
        # Handle food log input
        if 'food_amount' in request.form:
            food_amount = int(request.form['food_amount'])
            timestamp = datetime.now().isoformat()
            log_food_entry(food_amount, timestamp)  # Log the data into Supabase
            return redirect(url_for('home'))  # Refresh the page

    return render_template("home.html", 
                           age_in_months=age_in_months, 
                           grams_of_food=remaining_food, 
                           already_fed_today=already_fed_today)


if __name__ == "__main__":
    app.run(debug=True)
