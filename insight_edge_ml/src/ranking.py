import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/processed_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "../models/investment_ranking.pkl")

# Load data
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Processed dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print("✅ Data loaded successfully")
    print("Columns in dataset:", df.columns.tolist())

    # Ensure required columns exist
    required_columns = ["monthly_income", "current_savings", "existing_loans_debts", "best_investment_plan"]
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"❌ Missing required column: {col}")

    return df

# Generate investment category if missing
def generate_investment_category(df):
    if "investment_category" not in df.columns:
        print("⚠️ 'investment_category' column not found. Generating based on financial data...")

        # If 'best_investment_plan' exists, use it as categorical encoding
        if "best_investment_plan" in df.columns:
            df["investment_category"] = df["best_investment_plan"].astype("category").cat.codes
        else:
            # Create a simple categorization based on financial thresholds
            df["investment_category"] = pd.cut(df["monthly_income"], 
                                               bins=[0, 10000, 30000, float("inf")], 
                                               labels=[0, 1, 2])  # 0 = Low, 1 = Medium, 2 = High
            df["investment_category"] = df["investment_category"].astype(int)

        print("✅ 'investment_category' successfully created.")

    return df

# Train investment ranking model
def train_model(df):
    # Ensure the investment category exists
    df = generate_investment_category(df)

    # Define features and target variable
    features = ["monthly_income", "current_savings", "existing_loans_debts"]
    target = "investment_category"

    X = df[features]
    y = df[target]

    # Handle missing values
    X.fillna(X.median(), inplace=True)
    y.fillna(y.mode()[0], inplace=True)

    # Standardize numerical features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Predictions & Evaluation
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n📊 Model Performance:")
    print(f"Random Forest Accuracy: {accuracy:.2f}")
    print("Classification Report:\n", classification_report(y_test, y_pred))

    # Save model
    joblib.dump(rf_model, MODEL_PATH)
    print(f"\n✅ Model saved successfully at: {MODEL_PATH}")

# Run training
if __name__ == "__main__":
    try:
        df = load_data()
        train_model(df)
    except Exception as e:
        print(f"❌ Error: {e}")
