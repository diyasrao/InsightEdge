import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/processed_data.csv")
MODEL_PATH_LINEAR = os.path.join(BASE_DIR, "../models/linear_regression.pkl")
MODEL_PATH_TREE = os.path.join(BASE_DIR, "../models/decision_tree.pkl")
MODEL_PATH_POLY = os.path.join(BASE_DIR, "../models/polynomial_regression.pkl")

# Load data
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Processed dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print("✅ Data loaded successfully")
    print("Columns in dataset:", df.columns.tolist())
    
    return df

# Train models
def train_models(df):
    # Selecting features and target variable
    features = ["current_savings", "existing_loans_debts"]
    target = "monthly_income"

    # Check if features exist
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        raise KeyError(f"❌ Missing columns in dataset: {missing_cols}")

    X = df[features]
    y = df[target]

    # Handle missing values
    X.fillna(X.median(), inplace=True)
    y.fillna(y.median(), inplace=True)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train Linear Regression
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)

    # Train Decision Tree Regression
    tree_model = DecisionTreeRegressor(max_depth=5)
    tree_model.fit(X_train, y_train)

    # Train Polynomial Regression (Optional)
    poly = PolynomialFeatures(degree=2)
    X_poly_train = poly.fit_transform(X_train)
    X_poly_test = poly.transform(X_test)

    poly_model = LinearRegression()
    poly_model.fit(X_poly_train, y_train)

    # Predictions
    y_pred_linear = linear_model.predict(X_test)
    y_pred_tree = tree_model.predict(X_test)
    y_pred_poly = poly_model.predict(X_poly_test)

    # Model Evaluation
    print("\n📊 Model Performance:")
    print(f"Linear Regression MAE: {mean_absolute_error(y_test, y_pred_linear):.2f}")
    print(f"Decision Tree MAE: {mean_absolute_error(y_test, y_pred_tree):.2f}")
    print(f"Polynomial Regression MAE: {mean_absolute_error(y_test, y_pred_poly):.2f}")

    # Save models
    joblib.dump(linear_model, MODEL_PATH_LINEAR)
    joblib.dump(tree_model, MODEL_PATH_TREE)
    joblib.dump(poly_model, MODEL_PATH_POLY)

    print(f"\n✅ Models saved successfully at:\n- {MODEL_PATH_LINEAR}\n- {MODEL_PATH_TREE}\n- {MODEL_PATH_POLY}")

# Run training
if __name__ == "__main__":
    try:
        df = load_data()
        train_models(df)
    except Exception as e:
        print(f"❌ Error: {e}")
