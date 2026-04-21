"""
Finance Agent
─────────────
Predicts revenue impact and estimates improvement potential if all platforms
migrated to the winner's performance level.
"""


class FinanceAgent:
    def __init__(self, metrics: dict, winner: str):
        self.metrics = metrics
        self.winner  = winner

    def run(self) -> dict:
        winner_rev = self.metrics[self.winner]["avg_revenue"]
        all_revs   = {p: m["avg_revenue"] for p, m in self.metrics.items()}

        worst_platform  = min(all_revs, key=all_revs.get)
        worst_rev       = all_revs[worst_platform]

        uplift_pct = ((winner_rev - worst_rev) / worst_rev) * 100 if worst_rev else 0

        # Estimate total revenue if every platform matched winner's avg revenue
        total_users   = sum(m["total_users"]   for m in self.metrics.values())
        current_total = sum(m["total_revenue"] for m in self.metrics.values())
        projected     = total_users * winner_rev

        return {
            "winner_avg_rev":  round(winner_rev, 2),
            "worst_platform":  worst_platform,
            "worst_avg_rev":   round(worst_rev, 2),
            "uplift_pct":      round(uplift_pct, 2),
            "current_total":   round(current_total, 2),
            "projected_total": round(projected, 2),
            "improvement":     round(projected - current_total, 2),
        }
