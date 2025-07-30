import yaml
from pathlib import Path

BLOCKLIST_FILE = Path(__file__).resolve().parents[1] / "rules/blocklist.yaml"

def load_blocked_agents():
    try:
        with open(BLOCKLIST_FILE, "r") as f:
            config = yaml.safe_load(f)
            return set(config.get("blocked_agents", []))
    except Exception:
        return set()

def save_blocked_agents(agent_set):
    with open(BLOCKLIST_FILE, "w") as f:
        yaml.dump({"blocked_agents": sorted(agent_set)}, f)
