import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import joblib

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/processed_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "../models/kmeans_model.pkl")
DBSCAN_MODEL_PATH = os.path.join(BASE_DIR, "../models/dbscan_model.pkl")

# Load preprocessed data
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Processed dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print("✅ Data loaded successfully")
    print("Columns in dataset:", df.columns.tolist())
    
    return df

# Clustering function
def perform_clustering(df):
    # Selecting relevant numerical features
    features = ["monthly_income", "current_savings", "existing_loans_debts"]
    
    # Check if features exist
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        raise KeyError(f"❌ Missing columns in dataset: {missing_cols}")

    X = df[features]

    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["Cluster_KMeans"] = kmeans.fit_predict(X_scaled)

    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=0.7, min_samples=5)
    df["Cluster_DBSCAN"] = dbscan.fit_predict(X_scaled)

    return df, kmeans, dbscan

# Run clustering
if __name__ == "__main__":
    try:
        df = load_data()
        df_clustered, kmeans_model, dbscan_model = perform_clustering(df)
        
        # Save processed data
        df_clustered.to_csv(DATA_PATH, index=False)
        
        # Save models
        joblib.dump(kmeans_model, MODEL_PATH)
        joblib.dump(dbscan_model, DBSCAN_MODEL_PATH)
        
        print(f"✅ Clustering completed! Results saved at {DATA_PATH}")
        print(f"✅ K-Means model saved at {MODEL_PATH}")
        print(f"✅ DBSCAN model saved at {DBSCAN_MODEL_PATH}")

    except Exception as e:
        print(f"❌ Error: {e}")
