from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Function to calculate the dog's age in days and months
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

# Set Injeolmi's birthday
injeolmi_birthday = "2024-07-01"

@app.route('/')
def home():
    # Calculate age in days and months
    age_in_days = (datetime.today() - datetime.strptime(injeolmi_birthday, "%Y-%m-%d")).days
    age_in_months = calculate_age_in_months(injeolmi_birthday)
    grams_of_food = calculate_food_amount(age_in_days)
    
    # Render the template
    return render_template("home.html", age_in_months=age_in_months, grams_of_food=grams_of_food)

if __name__ == "__main__":
    app.run(debug=True)
