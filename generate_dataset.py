import pandas as pd
import random

df = pd.read_csv("data/important_attack_patterns_scored.csv")

rows = []

def generate_infra_features():
    environment = random.choice([0, 1, 2]) # 0=dev, 1=staging, 2=prod

    public_exposure = random.choice([0, 1])
    encryption_disabled = random.choice([0, 1])
    privilege_level = random.choice([0, 1, 2]) # 0=user, 1=admin, 2=system
    
    port_risk = random.choice([0, 1, 2])  # 0=low, 1=medium, 2=high
    history_incidents = random.randint(0, 5)

    return (
        environment,
        public_exposure,
        encryption_disabled,
        privilege_level,
        port_risk,
        history_incidents,
    ) 

def compute_risk(env, exposure, encryption, privilege, incidents, mitre_score):
     # HIGH RISK
    if (
        (env == 2 and exposure == 1 and mitre_score >= 4)
        or (encryption == 1 and privilege == 2 and mitre_score >= 4)
        or (incidents >= 4 and mitre_score >= 4)
    ):
        return 2

    # MEDIUM RISK
    if (
        (env == 1 and mitre_score >= 3)
        or exposure == 1
        or privilege == 1
        or mitre_score == 3
    ):
        return 1

    # LOW RISK
    return 0


def apply_contextual_noise(env, exposure, encryption, privilege, incidents, mitre_score, risk):

    noise_prob = 0.10

    # Medium ↔ High borderline
    if risk == 1 and mitre_score == 4 and env == 2:
        if random.random() < noise_prob:
            return 2

    # High borderline downgrade
    if risk == 2 and mitre_score == 4:
        if random.random() < noise_prob:
            return 1

    # Medium ↔ Low borderline
    if risk == 1 and mitre_score == 3 and exposure == 0:
        if random.random() < noise_prob:
            return 0

    return risk

for _ in range(5000):
    threat_row = df.sample(1).iloc[0]
    mitre_score = threat_row["mitre_tactic_score"]

    env, exposure, encryption, privilege, port_risk, incidents = generate_infra_features()

    risk = compute_risk(env, exposure, encryption, privilege, incidents, mitre_score)
    risk = apply_contextual_noise(env, exposure, encryption, privilege, incidents, mitre_score, risk)

    rows.append({
        "mitre_tactic_score": mitre_score,
        "environment": env,
        "public_exposure": exposure,
        "encryption_disabled": encryption,
        "privilege_level": privilege,
        "port_risk": port_risk,
        "history_incidents": incidents,
        "risk_level": risk
    })

df_final = pd.DataFrame(rows)
df_final.to_csv("data/synthetic_data.csv", index=False)

print(df_final["risk_level"].value_counts())