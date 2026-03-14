package devsecops

deny contains msg if {
    input.environment == "prod"
    input.public_exposure == 1
    msg := "Public exposure not allowed in production"
}

deny contains msg if {
    input.encryption_disabled == 1
    msg := "Encryption must be enabled"
}

deny contains msg if {
    input.privilege_level >= 2
    msg := "System-level privilege is too risky"
}

deny contains msg if {
    input.mitre_tactic_score >= 4
    msg := "High MITRE tactic risk detected"
}

deny contains msg if {
    input.history_incidents >= 4
    msg := "Deployment associated with repeated incidents"
}

