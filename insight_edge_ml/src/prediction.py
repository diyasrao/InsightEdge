import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

def load_data(filepath="../data/clustered_data.csv"):
    """Load clustered data."""
    return pd.read_csv(filepath)

def train_model(df):
    """Train a regression model for income prediction."""
    X = df.drop(columns=['Income'])  # Features
    y = df['Income']  # Target variable
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    joblib.dump(model, "../models/income_prediction.pkl")
    print("✅ Model trained and saved!")

if __name__ == "__main__":
    df = load_data()
    train_model(df)
