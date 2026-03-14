import pandas as pd

tactic_weights = {
    "initial-access": 5,
    "privilege-escalation": 5,
    "impact": 5,

    "credential-access": 4,
    "lateral-movement": 4,
    "command-and-control": 4,

    "defense-evasion": 3,
    "persistence": 3,
    "execution": 3,

    "discovery": 2,
    "collection": 2,
    "exfiltration": 4,

    "reconnaissance": 1,
    "resource-development": 1
}

def calculate_mitre_score(phase_string):
    phases = phase_string.split(",")
    weights = [tactic_weights.get(p.strip(), 0) for p in phases]
    return max(weights) if weights else 0

df = pd.read_csv("data/important_attack_patterns.csv")

df["mitre_tactic_score"] = df["phases"].apply(calculate_mitre_score)
print(df["mitre_tactic_score"].value_counts())

df.to_csv("data/important_attack_patterns_scored.csv", index=False)
print("file created...")