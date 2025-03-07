import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def load_data(filepath="../data/clustered_data.csv"):
    """Load clustered data."""
    return pd.read_csv(filepath)

def train_ranking_model(df):
    """Train a ranking model using Random Forest."""
    X = df.drop(columns=['Best_Investment'])  # Features
    y = df['Best_Investment']  # Target variable
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, "../models/investment_ranking.pkl")
    print("✅ Investment ranking model trained and saved!")

if __name__ == "__main__":
    df = load_data()
    train_ranking_model(df)
