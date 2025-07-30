# sentinelmesh/cli/sentinel_cli.py

import sys
import json
from time import sleep
from pathlib import Path

# Add project root to path for clean imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sentinelmesh.rules.rule_engine import check_all_rules
from sentinelmesh.monitor.agent_tracker import AgentTracker

LOG_FILE = Path(__file__).resolve().parents[1] / "logs/mcp_traffic.log"

def tail_log():
    seen = set()
    tracker = AgentTracker()

    while True:
        if not LOG_FILE.exists():
            sleep(1)
            continue

        with open(LOG_FILE, "r") as f:
            for line in f:
                if line in seen:
                    continue
                seen.add(line)

                try:
                    msg = json.loads(line)
                    sender = msg.get("sender", "unknown")
                    receiver = msg.get("receiver", "unknown")

                    # Record agent communication
                    tracker.record_message(sender, receiver)

                    # Security rules
                    alerts, risk = check_all_rules(msg)
                    if alerts:
                        print(f"\n⚠️ ALERT for message: {sender} ➡️ {receiver}")
                        for alert in alerts:
                            print(f"   → {alert}")
                        print(f"   🔥 Risk Score: {risk}/100")
                        if risk >= 80:
                            print("   🚨 SEVERE: Immediate review recommended.")
                        elif risk >= 50:
                            print("   ⚠️ Moderate risk.")
                        else:
                            print("   ✅ Low risk.")


                    # Agent-based heuristics
                    if tracker.is_new_sender(sender):
                        print(f"⚠️ New sender detected: {sender}")

                    if tracker.is_suspicious_volume(sender):
                        count = len(tracker.agent_history[sender])
                        print(f"🚨 High volume from {sender} — {count} messages observed.")

                except json.JSONDecodeError:
                    continue

        sleep(2)

def main():
    print("🔍 SentinelMesh MCP Monitor Running...\n")
    tail_log()

if __name__ == "__main__":
    main()

