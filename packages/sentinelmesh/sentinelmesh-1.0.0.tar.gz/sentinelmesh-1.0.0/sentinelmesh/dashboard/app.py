# sentinelmesh/dashboard/app.py

import json
import time
import pandas as pd
import streamlit as st
from pathlib import Path
from risk_engine import calculate_risk
from blocklist import load_blocked_agents, save_blocked_agents

LOG_FILE = Path(__file__).resolve().parents[1] / "logs/mcp_traffic.log"

st.set_page_config(page_title="SentinelMesh Dashboard", layout="wide")
st.title("🛡️ SentinelMesh Dashboard")
st.caption("Real-time Monitoring of MCP Agent Communication")

# Load log file
def load_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame()

    data = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                msg = json.loads(line)
                data.append({
                    "Timestamp": msg.get("timestamp"),
                    "Sender": msg.get("sender"),
                    "Receiver": msg.get("receiver"),
                    "Context": msg.get("context"),
                    "Payload": msg.get("payload")
                })
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(data)

# Load and clean logs
df = load_logs()

# Calculate risk early for full agent visibility
df["Risk"] = df.apply(calculate_risk, axis=1) if not df.empty else 0
AUTO_BLOCK_THRESHOLD = 90
high_risk_agents = set(df[df["Risk"] >= AUTO_BLOCK_THRESHOLD]["Sender"].unique())

# Sidebar filters
st.sidebar.header("🔍 Filters")
agent_filter = st.sidebar.text_input("Filter by Agent (sender or receiver)")
max_rows = st.sidebar.slider("Max rows", 10, 1000, 100)

# Quarantine UI
st.sidebar.header("🚫 Quarantine Controls")
all_agents = df["Sender"].unique().tolist() if not df.empty else []
manual_blocked_agents = load_blocked_agents()

# Show auto-quarantined agents (but not lock them in)
preselected_blocked = sorted(set(manual_blocked_agents).union(high_risk_agents))
selected = st.sidebar.multiselect(
    "Select agents to block", options=all_agents, default=preselected_blocked
)

# Save only manual changes
new_manual_blocklist = set(selected).intersection(all_agents) - high_risk_agents
if new_manual_blocklist != set(manual_blocked_agents):
    save_blocked_agents(new_manual_blocklist)
    st.sidebar.success("✅ Blocklist updated. Refreshing...")
    st.rerun()

# Timestamp cleaning and parsing
if not df.empty:
    if agent_filter:
        df = df[
            df["Sender"].str.contains(agent_filter, case=False) |
            df["Receiver"].str.contains(agent_filter, case=False)
        ]

    before = len(df)
    df["Timestamp"] = (
        df["Timestamp"]
        .astype(str)
        .str.strip()
        .str.replace(r"\+00:00$", "", regex=True)
    )
    df["ParsedTimestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce").dt.tz_localize("UTC")
    dropped_rows = df[df["ParsedTimestamp"].isna()]
    if not dropped_rows.empty:
        st.warning(f"{len(dropped_rows)} messages could not be parsed:")
        st.code(dropped_rows[["Timestamp", "Sender", "Payload"]].to_string(index=False))
    df = df.dropna(subset=["ParsedTimestamp"])
    df["Timestamp"] = df["ParsedTimestamp"]
    df.drop(columns=["ParsedTimestamp"], inplace=True)

    after = len(df)
    dropped = before - after
    if dropped > 0:
        st.warning(f"{dropped} messages were dropped due to invalid or unparsable timestamps.")

    if not df.empty:
        # Final blocklist from selection only (auto is advisory)
        final_blocklist = set(selected)
        df = df[~df["Sender"].isin(final_blocklist)]
        df = df.sort_values("Timestamp", ascending=False).head(max_rows)

        def highlight_risk_cell(val):
            if val >= 80:
                return "background-color: #ff4d4d; color: black"
            elif val >= 50:
                return "background-color: #ffa94d; color: black"
            elif val > 0:
                return "background-color: #ffff99; color: black"
            else:
                return "background-color: #b6fcb6; color: black"

        st.markdown("""
        **🧠 Risk Color Legend:**
        - 🔴 High (80–100)
        - 🟠 Moderate (50–79)
        - 🟡 Low (1–49)
        - 🟢 Safe (0)
        """)

        if "Risk" in df.columns:
            styled_df = df.style.map(highlight_risk_cell, subset=["Risk"])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No messages available to score.")

        st.success(f"✅ Displaying {len(df)} messages")

        st.subheader("📊 Agent Message Volume")
        try:
            if "Sender" in df.columns:
                volume_counts = df["Sender"].value_counts()
                if not volume_counts.empty:
                    volume_df = volume_counts.reset_index()
                    volume_df.columns = ["Agent", "Messages"]
                    st.bar_chart(volume_df.set_index("Agent"))
                else:
                    st.info("No agent message data available.")
        except Exception as e:
            st.error(f"Agent volume chart failed to render: {e}")

        st.subheader("🌡️ Risk Score Over Time")
        if "Risk" in df.columns:
            time_risk = df[["Timestamp", "Risk"]].set_index("Timestamp").sort_index()
            st.line_chart(time_risk.rolling(window=2).mean())
        else:
            st.info("No risk data available for chart.")

        st.subheader("🔵 Agent Risk Overview")
        avg_risk = df.groupby("Sender")["Risk"].agg(["count", "mean"]).reset_index()
        avg_risk = avg_risk.rename(columns={"Sender": "Agent", "count": "Messages", "mean": "Avg Risk"})
        alerts = df[df["Risk"] >= 50].groupby("Sender")["Risk"].count().reset_index()
        alerts = alerts.rename(columns={"Sender": "Agent", "Risk": "Alerts"})
        summary = pd.merge(avg_risk, alerts, on="Agent", how="left").fillna(0)
        summary["Alerts"] = summary["Alerts"].astype(int)
        summary = summary.sort_values("Avg Risk", ascending=False)
        st.dataframe(summary, use_container_width=True)

    else:
        st.warning("All messages were dropped after timestamp parsing.")
else:
    st.warning("No logs found. Run MCP sniffer to generate traffic.")

# Refresh every 5 seconds
st.caption("⏳ Refreshing in 5 seconds...")
time.sleep(5)
st.rerun()