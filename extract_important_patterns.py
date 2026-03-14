import json
import os
import pandas as pd

dataset_path = "../enterprise-attack"

all_objects = []
for file in os.listdir(dataset_path):
    path = os.path.join(dataset_path, file)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_objects.extend(data["objects"])

attack_patterns = []
for obj in all_objects:
    if obj["type"] == "attack-pattern":
        attack_patterns.append(obj)

# attack_phases = set()
# for attack_pattern in attack_patterns:
#     for kill_chain_phase in attack_pattern.get("kill_chain_phases", []):
#         attack_phases.add(kill_chain_phase["phase_name"])

clean_patterns = []

for ap in attack_patterns:
    revoked = ap.get("revoked", False)
    deprecated = ap.get("x_mitre_deprecated", False)

    if not revoked and not deprecated:
        clean_patterns.append(ap)

rows = []
for ap in clean_patterns:
    technique_id = None
    for ref in ap.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            technique_id = ref.get("external_id")
            break

    phases = [p["phase_name"] for p in ap.get("kill_chain_phases", [])]
    permissions = ap.get("x_mitre_permissions_required") or []
    permissions_str = ",".join(permissions) if permissions else "None"

    row = {
        "technique_id": technique_id,
        "name": ap.get("name"),
        "phases": ",".join(phases),
        "platforms": ",".join(ap.get("x_mitre_platforms", [])),
        "permissions": permissions_str
    }

    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("data/important_attack_patterns.csv", index=False)