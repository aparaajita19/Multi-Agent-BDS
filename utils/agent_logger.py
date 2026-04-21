"""
Agent Logger
────────────
Tracks each agent's execution: start time, end time, duration, and output summary.
Used to display the audit trail in the dashboard and export reports.
"""

import time
from datetime import datetime
from typing import Any


class AgentLogger:
    def __init__(self):
        self.logs: list[dict] = []
        self._start_times: dict[str, float] = {}

    def start(self, agent_name: str):
        self._start_times[agent_name] = time.time()
        self.logs.append({
            "agent":     agent_name,
            "status":    "running",
            "started_at": datetime.now().strftime("%H:%M:%S"),
            "ended_at":  None,
            "duration_s": None,
            "summary":   None,
        })

    def done(self, agent_name: str, summary: str):
        elapsed = round(time.time() - self._start_times.get(agent_name, time.time()), 2)
        for log in self.logs:
            if log["agent"] == agent_name and log["status"] == "running":
                log["status"]    = "done"
                log["ended_at"]  = datetime.now().strftime("%H:%M:%S")
                log["duration_s"] = elapsed
                log["summary"]   = summary
                break

    def to_dataframe(self):
        import pandas as pd
        return pd.DataFrame(self.logs)
