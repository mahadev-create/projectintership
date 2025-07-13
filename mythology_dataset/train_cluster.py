import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import joblib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
USER_DATA_CSV = os.path.join(ROOT, "../user_data.csv")
MODEL_PATH = os.path.join(ROOT, "kmeans_model.joblib")
ENCODER_PATH = os.path.join(ROOT, "label_encoders.joblib")

def load_and_preprocess():
    df = pd.read_csv(USER_DATA_CSV)

    # Features: 4 astro + 10 personality
    cols = ["Zodiac", "Moon_Sign", "Nakshatra", "Ganam"] + [f"Q{i+1}" for i in range(10)]
    df = df[cols]

    # Encode
    encoders = {}
    for col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    return df, encoders

def train_and_save_model(n_clusters=20):
    df, encoders = load_and_preprocess()
    n_clusters = min(n_clusters, len(df))  # Safety check
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(df)

    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    print(f"✅ KMeans model saved to {MODEL_PATH}")
    print(f"🧠 Encoders saved to {ENCODER_PATH}")

if __name__ == "__main__":
    train_and_save_model()
