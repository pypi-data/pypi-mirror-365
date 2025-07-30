# 🛡️ SentinelMesh

![CI](https://github.com/rishit03/SentinelMesh/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

**SentinelMesh** is a real-time security, policy, and observability mesh for AI agents communicating via the Model Context Protocol (MCP).

---

## 🚀 Features

- 🔎 Real-time monitoring of MCP agent-to-agent messages
- 🔐 Prompt injection & sensitive context detection (YAML-defined rules)
- ⚠️ Risk scoring with visual color tags
- 📊 Streamlit dashboard with filters, charts, and risk summaries
- 🧪 Log replay tool for forensic analysis
- 🛑 Manual + auto-quarantine via blocklist
- 🧱 Modular CLI structure (installed with `setup.py`)

---

## 📦 Installation

From your project root:

```bash
pip install -e .
```

---

## 🖥️ Dashboard

Launch the real-time Streamlit dashboard:

```bash
streamlit run sentinelmesh/dashboard/app.py
```

Features:
- Realtime log table
- Risk scoring with heatmap
- Agent volume and risk timeline
- Block/unblock agents live from the sidebar

---

## 🧰 CLI Tools

### MCP Monitor:

```bash
sentinelmesh-cli
```

Monitors the log file and shows alerts in real time.

---

### Log Replay:

```bash
sentinelmesh-replay --agent agent.hrbot.local --limit 10
```

Replay historical logs with filters.

---

## ⚙️ Config Files

- `sentinelmesh/rules/rules.yaml` — security rules (phrases, context, regex)
- `sentinelmesh/rules/blocklist.yaml` — blocked agents (manually set)
- `sentinelmesh/logs/mcp_traffic.log` — live traffic log

---

## 📝 License

MIT © Rishit Goel
