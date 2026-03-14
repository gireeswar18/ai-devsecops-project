import pandas as pd

df = pd.read_csv('data/synthetic_data.csv')

df["env_prod"] = df["environment"].apply(lambda x: 1 if x == 2 else 0)
df["high_privilege"] = df["privilege_level"].apply(lambda x: 1 if x == 2 else 0)
df["threat_exposure_score"] = df["mitre_tactic_score"] * df["public_exposure"]
df["mitre_score_norm"] = (df["mitre_tactic_score"] - 1) / 4

df.to_csv("data/feature_engineered_dataset.csv", index=False)

print(df.head())
print(df.describe())