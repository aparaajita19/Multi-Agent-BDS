"""
Decision Agent
──────────────
Compares platform performance using a weighted composite score:
  Score = (normalised avg_revenue × rev_weight) + (normalised conversion_rate × conv_weight)

Weights are configurable from the Streamlit sidebar.
"""


class DecisionAgent:
    def __init__(self, metrics: dict,
                 rev_weight: float  = 0.60,
                 conv_weight: float = 0.40):
        self.metrics     = metrics
        self.rev_weight  = rev_weight
        self.conv_weight = conv_weight

    def _normalise(self, values: list) -> list:
        mn, mx = min(values), max(values)
        if mx == mn:
            return [1.0] * len(values)
        return [(v - mn) / (mx - mn) for v in values]

    def run(self) -> dict:
        platforms = list(self.metrics.keys())
        rev_vals  = [self.metrics[p]["avg_revenue"]    for p in platforms]
        conv_vals = [self.metrics[p]["conversion_rate"] for p in platforms]

        norm_rev  = self._normalise(rev_vals)
        norm_conv = self._normalise(conv_vals)

        scores = {
            p: round(
                self.rev_weight  * norm_rev[i] +
                self.conv_weight * norm_conv[i],
                4,
            )
            for i, p in enumerate(platforms)
        }

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner = ranked[0][0]

        return {
            "winner":  winner,
            "scores":  scores,
            "ranking": ranked,
        }
