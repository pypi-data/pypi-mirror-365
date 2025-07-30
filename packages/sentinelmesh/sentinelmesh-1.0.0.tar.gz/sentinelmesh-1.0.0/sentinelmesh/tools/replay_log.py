# sentinelmesh/tools/replay_log.py

import json
import argparse
from pathlib import Path

# FIXED: Correct relative path to the log file
LOG_FILE = Path(__file__).resolve().parents[1] / "logs/mcp_traffic.log"

def replay_log(filter_agent=None, limit=None):
    if not LOG_FILE.exists():
        print("❌ Log file not found.")
        return

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    print("🎬 Replaying MCP Traffic Log:\n")
    count = 0

    for line in lines:
        try:
            msg = json.loads(line)
            sender = msg.get("sender")
            receiver = msg.get("receiver")
            context = msg.get("context")
            payload = msg.get("payload")
            timestamp = msg.get("timestamp")

            if filter_agent and filter_agent not in (sender, receiver):
                continue

            print(f"[{timestamp}] {sender} ➡️ {receiver}")
            print(f"    Context: {context}")
            print(f"    Payload: {payload}\n")

            count += 1
            if limit and count >= limit:
                break

        except json.JSONDecodeError:
            continue

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Replay MCP traffic from logs.")
    parser.add_argument("--agent", help="Filter by agent ID")
    parser.add_argument("--limit", type=int, help="Max messages to display")
    args = parser.parse_args()
    replay_log(filter_agent=args.agent, limit=args.limit)

if __name__ == "__main__":
    main()

