# # predict_persona.py

# import pandas as pd
# import joblib
# from sklearn.preprocessing import LabelEncoder
# import os

# ROOT = os.path.dirname(os.path.abspath(__file__))
# USER_DATA_CSV = os.path.join(ROOT, "../user_data.csv")
# MODEL_PATH = os.path.join(ROOT, "kmeans_model.joblib")
# CLUSTER_MAP_PATH = os.path.join(ROOT, "mythic_cluster_with_ids.csv")

# # 🔢 Encode last row's features
# def preprocess_input():
#     df = pd.read_csv(USER_DATA_CSV)
#     cols = ["Zodiac", "Moon_Sign", "Nakshatra", "Ganam"] + [f"Q{i+1}" for i in range(10)]
#     df = df[cols]

#     le = LabelEncoder()
#     for col in df.columns:
#         df[col] = le.fit_transform(df[col].astype(str))

#     return df.iloc[-1].values.reshape(1, -1)

# # 🔮 Predict cluster and fetch persona
# def predict_persona():
#     input_data = preprocess_input()

#     # Load trained KMeans model
#     model = joblib.load(MODEL_PATH)
#     cluster = model.predict(input_data)[0]

#     # Load persona map
#     map_df = pd.read_csv(CLUSTER_MAP_PATH)
#     persona = map_df[map_df["Cluster"] == cluster]

#     if persona.empty:
#         return {"error": f"No persona found for cluster {cluster}"}
    
#     return persona.iloc[0].to_dict()

# if __name__ == "__main__":
#     result = predict_persona()
#     print("🔮 Predicted Persona:", result)

import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
import os

# Paths



ROOT = os.path.dirname(os.path.abspath(__file__))

# ✅ Points to: MythicPersona/user_data.csv
USER_DATA_CSV = os.path.join(ROOT, "../user_data.csv")

# ✅ Points to: MythicPersona/mythology_dataset/kmeans_model.joblib
MODEL_PATH = os.path.join(ROOT, "../mythology_dataset/kmeans_model.joblib")

# ✅ Points to: MythicPersona/mythic_cluster_with_ids.csv
CLUSTER_MAP_PATH = os.path.join(ROOT, "../mythic_clusters_with_ids.csv")


# 🔢 Encode last row's features from user_data.csv
def preprocess_input():
    df = pd.read_csv(USER_DATA_CSV)
    cols = ["Zodiac", "Moon_Sign", "Nakshatra", "Ganam"] + [f"Q{i+1}" for i in range(10)]

    # Ensure required columns exist
    if not all(col in df.columns for col in cols):
        raise ValueError("CSV file is missing required columns.")

    df = df[cols]

    le = LabelEncoder()
    for col in df.columns:
        df[col] = le.fit_transform(df[col].astype(str))

    return df.iloc[-1].values.reshape(1, -1)

# 🔮 Predict cluster and fetch persona from map
def match_persona():
    input_data = preprocess_input()

    model = joblib.load(MODEL_PATH)
    cluster = model.predict(input_data)[0]

    persona_df = pd.read_csv(CLUSTER_MAP_PATH)
    match = persona_df[persona_df["cluster_id"] == cluster]

    if match.empty:
        return {"error": f"No persona found for cluster {cluster}"}

    return match.iloc[0].to_dict()
