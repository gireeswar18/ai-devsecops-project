import joblib
import numpy as np
import pandas as pd
import shap
import yaml

model = joblib.load("data/trained_model.pkl")
explainer = shap.TreeExplainer(model)

with open("policy.yaml", "r") as f:
    policies = yaml.safe_load(f)

ENV_THRESHOLDS = {"dev": 0.85, "staging": 0.65, "prod": 0.40}
FEATURE_ORDER = [
    "mitre_tactic_score",
    "environment",
    "public_exposure",
    "encryption_disabled",
    "privilege_level",
    "port_risk",
    "history_incidents",
    "env_prod",
    "high_privilege",
    "threat_exposure_score",
    "mitre_score_norm",
]

def evaluate_policy(input_features: dict):

    for rule in policies["rules"]:
        cond = rule["condition"]

        # Match environment
        if "environment" in cond:
            if input_features["environment"] != cond["environment"]:
                continue

        # Match public exposure
        if "public_exposure" in cond:
            if input_features["public_exposure"] != cond["public_exposure"]:
                continue

        # Match MITRE score
        if "mitre_tactic_score" in cond:
            if input_features["mitre_tactic_score"] != cond["mitre_tactic_score"]:
                continue

        return "BLOCK"

    return "ALLOW"


def evaluate_risk(input_features: dict):
    env_map = {0: "dev", 1: "staging", 2: "prod"}

    environment = input_features["environment"]
    env_name = env_map[environment]

    threshold = ENV_THRESHOLDS[env_name]

    # Base features (numeric, same as training)
    mitre_score = input_features["mitre_tactic_score"]
    public_exposure = input_features["public_exposure"]
    encryption_disabled = input_features["encryption_disabled"]
    privilege_level = input_features["privilege_level"]
    port_risk = input_features["port_risk"]
    history_incidents = input_features["history_incidents"]

    # ---- Recreate Engineered Features ----
    env_prod = 1 if environment == 2 else 0
    high_privilege = 1 if privilege_level == 2 else 0
    threat_exposure_score = mitre_score * public_exposure
    mitre_score_norm = (mitre_score - 1) / 4

    feature_vector = np.array(
        [
            [
                mitre_score,
                environment,
                public_exposure,
                encryption_disabled,
                privilege_level,
                port_risk,
                history_incidents,
                env_prod,
                high_privilege,
                threat_exposure_score,
                mitre_score_norm,
            ]
        ]
    )

    probabilities = model.predict_proba(feature_vector)[0]
    high_risk_prob = probabilities[2]

    if high_risk_prob > threshold:
        decision = "BLOCK"
    else:
        decision = "ALLOW"

    # print(
    #     "Low:", probabilities[0], "Medium:", probabilities[1], "High:", probabilities[2]
    # )

    shap_values = explainer.shap_values(feature_vector)
    high_risk_shap = shap_values[0, :, 2]
    feature_contribution = {
        feature: float(value)
        for feature, value in zip(FEATURE_ORDER, high_risk_shap)
    }
    return {
        "high_risk_probability": float(probabilities[2]),
        "threshold": threshold,
        "decision": decision,
        "explanation": feature_contribution
    }


if __name__ == "__main__":
    sample = {
        "mitre_tactic_score": 3,
        "environment": 1,  # staging
        "public_exposure": 1,
        "encryption_disabled": 0,
        "privilege_level": 1,
        "port_risk": 1,
        "history_incidents": 2
    }

    ai_result = evaluate_risk(sample)
    policy_result = evaluate_policy(sample)

    if ai_result["decision"] == "BLOCK" or policy_result == "BLOCK":
        final_decision = "BLOCK"
    else:
        final_decision = "ALLOW"

    print("AI result:", ai_result)
    print("Policy result:", policy_result)
    print("Final Decision:", final_decision)