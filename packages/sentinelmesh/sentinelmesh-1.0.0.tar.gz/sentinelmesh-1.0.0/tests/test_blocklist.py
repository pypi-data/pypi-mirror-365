import os
import yaml
from sentinelmesh.dashboard.blocklist import load_blocked_agents, save_blocked_agents

TEST_BLOCKLIST_FILE = "tests/test_blocklist.yaml"

def test_save_and_load_blocked_agents(tmp_path, monkeypatch):
    # Arrange
    temp_file = tmp_path / "blocklist.yaml"
    monkeypatch.setattr("sentinelmesh.dashboard.blocklist.BLOCKLIST_FILE", temp_file)

    agents_to_block = {"agent.hrbot.local", "agent.slack.local"}
    save_blocked_agents(agents_to_block)

    # Act
    loaded = load_blocked_agents()

    # Assert
    assert loaded == agents_to_block
