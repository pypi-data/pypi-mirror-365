# sentinelmesh/rules/rule_engine.py

import yaml
import re
from pathlib import Path

RULE_FILE = Path(__file__).resolve().parent / "rules.yaml"

with open(RULE_FILE, "r") as f:
    config = yaml.safe_load(f)

rules = config.get("rules", [])

def check_all_rules(message):
    alerts = []
    total_risk = 0
    context = message.get("context", "")
    payload = message.get("payload", "")

    for rule in rules:
        rule_id = rule.get("id", "unknown")
        risk = rule.get("risk", 0)

        if rule["type"] == "context_block":
            if context in rule["match"]:
                alerts.append(f"🔒 Context '{context}' is blocked by policy [{rule_id}]")
                total_risk += risk

        elif rule["type"] == "payload_contains":
            for phrase in rule["match"]:
                if phrase.lower() in payload.lower():
                    alerts.append(f"🚨 Payload matched forbidden phrase: '{phrase}' [{rule_id}]")
                    total_risk += risk

        elif rule["type"] == "payload_regex":
            pattern = rule["pattern"]
            if re.search(pattern, payload):
                alerts.append(f"⚠️ Payload matched regex pattern: '{pattern}' [{rule_id}]")
                total_risk += risk

    return alerts, min(total_risk, 100)

