import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt

def load_data(filepath="../data/processed_data.csv"):
    """Load preprocessed data."""
    return pd.read_csv(filepath)

def apply_kmeans(df, n_clusters=3):
    """Apply K-Means clustering."""
    model = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = model.fit_predict(df.select_dtypes(include=['number']))
    return df, model

if __name__ == "__main__":
    df = load_data()
    df, model = apply_kmeans(df)
    df.to_csv("../data/clustered_data.csv", index=False)
    print("✅ Clustering done and saved!")
