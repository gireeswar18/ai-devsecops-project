STAGE 1:
Review file structure   
file
    - objects
        - object
            - type: attack-pattern
                - keys: ['type', 'id', 'created_by_ref', 'created', 'modified', 'name', 'description', 'kill_chain_phases', 'external_references', 'object_marking_refs', 'x_mitre_data_sources', 'x_mitre_permissions_required', 'x_mitre_platforms', 'spec_version', 'x_mitre_attack_spec_version', 'x_mitre_domains', 'x_mitre_modified_by_ref', 'x_mitre_version']
STAGE 2:
    Raw STIX JSON files
            ↓
    Load all objects
            ↓
    Extract attack-pattern objects
            ↓
    Remove revoked / deprecated techniques
            ↓
    Extract structured fields
            ↓
    Save clean enterprise_attack_clean.csv

STAGE 3:

    enterprise_attack_clean.csv
            ↓
    Define tactic severity weights
            ↓
    Map each technique’s phases → weights
            ↓
    Take max(weight)
            ↓
    Add mitre_tactic_score column
            ↓
    Save enterprise_attack_scored.csv

STAGE 4 & 5:
    enterprise_attack_scored.csv
            ↓
    Sample techniques (with mitre_tactic_score)
            ↓
    Simulate deployment metadata
            ↓
    Combine threat + infra context
            ↓
    Generate risk label
            ↓
    synthetic_data.csv

STAGE 6:
    synthetic_data.csv
        ↓
    Add engineered features
            ↓
    Normalize only selected features
            ↓
    Create final training dataset

STAGE 7:
    feature_engineered_dataset.csv
        ↓
    Split features & target
            ↓
    Train/Test split
            ↓
    Train XGBoost multi-class model
            ↓
    Evaluate metrics
            ↓
    Save trained model

STAGE 8:
    Incoming Deployment Metadata
            ↓
    Feature Engineering (same pipeline as training)
            ↓
    Model.predict_proba()
            ↓
    Extract High-Risk Probability
            ↓
    Compare with Environment Threshold
            ↓
    ALLOW / BLOCK

STAGE 8:
    Incoming Deployment Metadata (JSON)
            ↓
    Extract Base Numeric Features
            ↓
    Recreate Engineered Features
        • env_prod
        • high_privilege
        • threat_exposure_score
        • mitre_score_norm
            ↓
    Build Feature Vector (Exact Training Order)
            ↓
    model.predict_proba()
            ↓
    Extract P(class = 2)  → High-Risk Probability
            ↓
    Map Environment (0/1/2 → dev/staging/prod)
            ↓
    Fetch Environment Threshold
        • dev → 0.85
        • staging → 0.65
        • prod → 0.40
            ↓
    Compare Probability vs Threshold
            ↓
    ALLOW  /  BLOCK

STAGE 9:
        Stage 8 Decision Computed
            ↓
    Create SHAP TreeExplainer (once, using trained model)
            ↓
    Pass Feature Vector to SHAP
        shap_values = explainer.shap_values(feature_vector)
            ↓
    Extract Class-2 SHAP Values
        shap_values[0, :, 2]
        (Explanation for HIGH risk class)
            ↓
    Map Feature Names → SHAP Contributions
            ↓
    Interpret Contribution Sign
        Positive → pushes toward HIGH risk
        Negative → pushes away from HIGH risk
            ↓
    Attach Explanation to Output JSON
            ↓
    AI now explains:
    WHY deployment was BLOCKED or ALLOWED

STAGE 10:
    Incoming Deployment Metadata
        ↓
    AI Risk Engine (Stage 8)
            ↓
    Deterministic Policy Evaluation (YAML Rules)
            ↓
    If (AI says BLOCK) OR (Policy says BLOCK)
            ↓
    Final Decision = BLOCK
    Else
            ↓
    Final Decision = ALLOW

    sample2 = {
        "mitre_tactic_score": 1,
        "environment": 0,  # dev
        "public_exposure": 0,
        "encryption_disabled": 0,
        "privilege_level": 0,
        "port_risk": 0,
        "history_incidents": 0
    }
    
    sample3 = {
        "mitre_tactic_score": 3,
        "environment": 1,  # staging
        "public_exposure": 1,
        "encryption_disabled": 0,
        "privilege_level": 1,
        "port_risk": 1,
        "history_incidents": 2
    }

STAGE 11:
    AI Risk Engine
        ↓
    High Risk? → BLOCK
        ↓
    Else
        ↓
    OPA Policy Check
        ↓
    If deny list NOT empty → BLOCK
    Else → ALLOW

    Start:
    opa run --server policy.rego

    Check request:
    curl.exe -X POST "http://localhost:8181/v1/data/devsecops/deny" `
    ∙ -H "Content-Type: application/json" `
    ∙ --data-binary "@input.json"

STAGE 12:
    Client Request
        │
        ▼
    FastAPI API
        │
        ├── AI Risk Engine (risk_engine.py)
        │
        └── OPA Policy Engine (REST API)
                │
                ▼
        Policy violations
                │
                ▼
            Final Decision
            ALLOW / BLOCK

STAGE 13:
    AI Risk Detection
    +
    OPA Policy Enforcement
    +
    REST API
    +
    Deployment Simulation
    +
    Swagger Documentation

STAGE 14:
    Client (Swagger / Bruno)
            │
            ▼
    FastAPI Container
    (AI Risk Engine)
            │
            ▼
    OPA Container
    (Policy Governance)
            │
            ▼
    Final Decision
    ALLOW / BLOCK

