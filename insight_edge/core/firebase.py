import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK (ensure this is done once in your project)
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()

# Function to add a user
def add_user(user_id, name, email, password_hash):
    db.collection("users").document(user_id).set({
        "name": name,
        "email": email,
        "password_hash": password_hash
    })

# Function to add financial data
def add_financial_data(financial_data_id, user_id, household_income, household_size, age, occupation, education_level, monthly_income, monthly_expenses):
    db.collection("financial_data").document(financial_data_id).set({
        "user_id": user_id,
        "household_income": household_income,
        "household_size": household_size,
        "age": age,
        "occupation": occupation,
        "education_level": education_level,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "savings": monthly_income - monthly_expenses
    })

# Function to add a recommendation
def add_recommendation(recommendation_id, user_id, plan_name, plan_details):
    db.collection("recommendations").document(recommendation_id).set({
        "user_id": user_id,
        "plan_name": plan_name,
        "plan_details": plan_details
    })

# Function to add a government scheme
def add_government_scheme(scheme_id, scheme_name, description, eligibility, link):
    db.collection("government_schemes").document(scheme_id).set({
        "scheme_name": scheme_name,
        "description": description,
        "eligibility": eligibility,
        "link": link
    })

# Example usage (for testing purposes)
if __name__ == "__main__":
    add_user("user_001", "John Doe", "john@example.com", "hashed_password")
    add_financial_data(
        "financial_001",
        "user_001",
        50000,
        4,
        30,
        "Teacher",
        "Graduate",
        50000,
        20000
    )
