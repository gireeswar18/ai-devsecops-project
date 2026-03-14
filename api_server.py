from fastapi import FastAPI
import requests
from deployment_input import DeploymentInput
from risk_engine import evaluate_risk
import random

app = FastAPI()

# OPA_URL = "http://localhost:8181/v1/data/devsecops/deny"
OPA_URL = "http://opa:8181/v1/data/devsecops/deny"

ENV_MAP = {
    "dev": 0,
    "staging": 1,
    "prod": 2
}

@app.post("/deploy/check")
def check_deployment(data: DeploymentInput):

    payload = data.dict()

    # convert environment for AI model
    payload["environment"] = ENV_MAP[payload["environment"]]

    # ---------- AI evaluation ----------
    ai_result = evaluate_risk(payload)

    # ---------- OPA evaluation ----------
    opa_response = requests.post(
        OPA_URL,
        json={"input": data.dict()}  # send original values to OPA
    )

    opa_result = opa_response.json()["result"]

    # ---------- Final decision ----------
    if ai_result["decision"] == "BLOCK" or len(opa_result) > 0:
        final_decision = "BLOCK"
    else:
        final_decision = "ALLOW"

    return {
        "ai_risk": ai_result,
        "opa_violations": opa_result,
        "final_decision": final_decision
    }

@app.get("/deploy/simulate")
def simulate_deployment():

    data = {
        "environment": random.choice(["dev","staging","prod"]),
        "public_exposure": random.randint(0,1),
        "encryption_disabled": random.randint(0,1),
        "privilege_level": random.randint(0,2),
        "port_risk": random.randint(0,2),
        "history_incidents": random.randint(0,5),
        "mitre_tactic_score": random.randint(1,5)
    }

    return check_deployment(DeploymentInput(**data))

@app.post("/risk/explain")
def explain_risk(data: DeploymentInput):

    payload = data.dict()

    payload["environment"] = ENV_MAP[payload["environment"]]

    result = evaluate_risk(payload)

    return {
        "risk_probability": result["high_risk_probability"],
        "explanation": result["explanation"]
    }