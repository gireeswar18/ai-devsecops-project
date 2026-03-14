from pydantic import BaseModel

class DeploymentInput(BaseModel):
    environment: str
    public_exposure: int
    encryption_disabled: int
    privilege_level: int
    port_risk: int
    history_incidents: int
    mitre_tactic_score: int