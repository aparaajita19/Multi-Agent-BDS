"""
Analyst Agent
─────────────
Processes the dataset and computes per-platform metrics:
  • Average Revenue
  • Conversion Rate
  • Total Users
  • Total Revenue
"""

import pandas as pd


class AnalystAgent:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def run(self) -> dict:
        """Return dict: { platform: { avg_revenue, conversion_rate, ... } }"""
        results = {}

        for platform, group in self.df.groupby("PLATFORM"):
            avg_rev  = group["REVENUE"].mean()
            total_rev = group["REVENUE"].sum()
            n_users  = len(group)

            # If CONVERTED column exists, use it; otherwise simulate from revenue
            if "CONVERTED" in group.columns:
                conv_rate = group["CONVERTED"].mean() * 100
            else:
                # Derive a synthetic conversion proxy (top 30% revenue = converted)
                threshold = group["REVENUE"].quantile(0.70)
                conv_rate = (group["REVENUE"] >= threshold).mean() * 100

            results[platform] = {
                "avg_revenue":     round(avg_rev, 2),
                "total_revenue":   round(total_rev, 2),
                "conversion_rate": round(conv_rate, 2),
                "total_users":     n_users,
            }

        return results
