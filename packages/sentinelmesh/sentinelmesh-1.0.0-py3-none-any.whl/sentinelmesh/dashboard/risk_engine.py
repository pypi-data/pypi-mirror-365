# sentinelmesh/dashboard/risk_engine.py

import yaml
import re
from pathlib import Path

RULE_FILE = Path(__file__).resolve().parents[1] / "rules/rules.yaml"

with open(RULE_FILE, "r") as f:
    config = yaml.safe_load(f)

rules = config.get("rules", [])

def calculate_risk(message):
    total_risk = 0
    context = message.get("Context", "")
    payload = message.get("Payload", "")

    for rule in rules:
        rule_type = rule.get("type")
        rule_id = rule.get("id", "unknown")
        risk = rule.get("risk", 0)

        if rule_type == "context_block":
            if context in rule.get("match", []):
                total_risk += risk

        elif rule_type == "payload_contains":
            for phrase in rule.get("match", []):
                if phrase.lower() in payload.lower():
                    total_risk += risk

        elif rule_type == "payload_regex":
            pattern = rule.get("pattern")
            if pattern and re.search(pattern, payload):
                total_risk += risk

    return min(total_risk, 100)
