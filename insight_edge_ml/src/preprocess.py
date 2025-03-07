import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "../data/insight_edge_financial_dataset.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "../data/processed_data.csv")

# Load dataset
def load_data():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset not found at {RAW_DATA_PATH}")
    
    df = pd.read_csv(RAW_DATA_PATH)
    print("✅ Data loaded successfully")
    print("Columns in dataset:", df.columns.tolist())
    
    return df

# Preprocessing function
def preprocess_data(df):
    # Convert column names to lowercase and remove spaces
    df.columns = df.columns.str.strip().str.lower()

    # Selecting necessary columns (modify based on your dataset)
    selected_columns = ['monthly_income', 'current_savings', 'existing_loans_debts', 'best_investment_plan']
    
    # Check if selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"❌ Missing columns in dataset: {missing_cols}")

    df = df[selected_columns]

    # Handle missing values
    df.fillna(df.median(numeric_only=True), inplace=True)

    # Convert categorical labels (if needed)
    if df["best_investment_plan"].dtype == 'object':
        df["best_investment_plan"] = df["best_investment_plan"].astype("category").cat.codes

    # Standardize numerical features
    scaler = StandardScaler()
    num_cols = ["monthly_income", "current_savings", "existing_loans_debts"]
    df[num_cols] = scaler.fit_transform(df[num_cols])

    return df

# Run preprocessing
if __name__ == "__main__":
    try:
        df = load_data()
        df_processed = preprocess_data(df)
        df_processed.to_csv(PROCESSED_DATA_PATH, index=False)
        print(f"✅ Preprocessed data saved at {PROCESSED_DATA_PATH}")
    except Exception as e:
        print(f"❌ Error: {e}")
