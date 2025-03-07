import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_data(filepath="insight_edge_ml\data\insight_edge_financial_dataset.csv"):
    """Load dataset from CSV file."""
    return pd.read_csv(filepath)

def preprocess_data(df):
    """Handle missing values and scale numerical data."""
    df = df.dropna()  # Remove missing values
    scaler = StandardScaler()
    numerical_cols = df.select_dtypes(include=['number']).columns
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    return df

if __name__ == "__main__":
    df = load_data()
    df = preprocess_data(df)
    df.to_csv("../data/processed_data.csv", index=False)
    print("✅ Data preprocessed and saved!")
