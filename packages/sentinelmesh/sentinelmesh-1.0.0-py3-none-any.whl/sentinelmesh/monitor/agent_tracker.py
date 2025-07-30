# sentinelmesh/monitor/agent_tracker.py

from collections import defaultdict
from datetime import datetime, timezone

class AgentTracker:
    def __init__(self):
        self.agent_history = defaultdict(list)  # {agent_id: [timestamps]}
        self.agent_pairs = defaultdict(int)     # {(sender, receiver): count}

    def record_message(self, sender, receiver):
        now = datetime.now(timezone.utc)
        self.agent_history[sender].append(now)
        self.agent_pairs[(sender, receiver)] += 1

    def get_message_count(self, sender, receiver):
        return self.agent_pairs.get((sender, receiver), 0)

    def is_new_sender(self, sender):
        return len(self.agent_history[sender]) == 1

    def is_suspicious_volume(self, sender, threshold=5):
        return len(self.agent_history[sender]) > threshold
