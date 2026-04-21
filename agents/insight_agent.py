"""
Insight Agent
─────────────
Uses Groq API to generate human-readable business insights
from the multi-agent output.

Groq API base URL : https://api.groq.com/openai/v1
Compatible models : llama-3.3-70b-versatile | llama3-8b-8192
"""

import os


class InsightAgent:
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    MODEL         = "llama-3.3-70b-versatile"   # swap to "llama3-8b-8192" for faster/cheaper

    def __init__(self, metrics: dict, decision: dict, finance: dict,
                 api_key: str | None = None):
        self.metrics  = metrics
        self.decision = decision
        self.finance  = finance
        self.api_key  = api_key or os.getenv("GROQ_API_KEY", "")

    # ── Build prompt ─────────────────────────────────────────────────────────
    def _build_prompt(self) -> str:
        winner = self.decision["winner"]
        ranked = self.decision["ranking"]
        fin    = self.finance

        platform_lines = "\n".join(
            f"  • {p}: avg revenue ₹{self.metrics[p]['avg_revenue']:,.0f}, "
            f"conversion {self.metrics[p]['conversion_rate']:.1f}%"
            for p in self.metrics
        )

        ranking_lines = "\n".join(
            f"  {i+1}. {p} (score {s:.3f})"
            for i, (p, s) in enumerate(ranked)
        )

        return f"""You are the Insight Agent in a multi-agent business intelligence system.

Platform comparison data:
{platform_lines}

Composite ranking (revenue 60% + conversion 40%):
{ranking_lines}

Winner: {winner}
Revenue uplift vs worst performer ({fin['worst_platform']}): +{fin['uplift_pct']:.1f}%
Projected revenue gain if all platforms match {winner}: ₹{fin['improvement']:,.0f}

Write a concise 3-paragraph business insight report:
1. Why {winner} is the recommended platform (cite specific numbers).
2. One concrete action the business should take immediately.
3. One risk or caveat to monitor going forward.

Use plain prose. No bullet points. No markdown headers. Be specific and data-driven."""

    # ── Call Groq API ─────────────────────────────────────────────────────────
    def run(self) -> str:
        if not self.api_key:
            return self._fallback()

        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key,
                base_url=self.GROQ_BASE_URL,
            )

            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert e-commerce business analyst. "
                            "Provide clear, actionable insights based on data."
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(),
                    },
                ],
                temperature=0.4,
                max_tokens=512,
            )

            return response.choices[0].message.content.strip()

        except Exception as exc:
            return (
                f"⚠️ Groq API error: {exc}\n\n"
                + self._fallback()
            )

    # ── Fallback (no API key) ─────────────────────────────────────────────────
    def _fallback(self) -> str:
        winner  = self.decision["winner"]
        fin     = self.finance
        ranked  = self.decision["ranking"]
        metrics = self.metrics

        return (
            f"**{winner}** leads the multi-platform comparison with an average revenue of "
            f"₹{metrics[winner]['avg_revenue']:,.0f} and a conversion rate of "
            f"{metrics[winner]['conversion_rate']:.1f}%, outperforming all other platforms "
            f"on the composite score.\n\n"
            f"The business should prioritise resource allocation toward {winner} "
            f"and study its customer journey to replicate success on "
            f"{ranked[-1][0]}, which currently lags by "
            f"+{fin['uplift_pct']:.1f}% in revenue per user.\n\n"
            f"Monitor seasonal demand shifts; platforms like Meesho and Myntra "
            f"may outperform during sale events even if they trail in baseline metrics. "
            f"*(Set GROQ_API_KEY in .streamlit/secrets.toml to get a full AI-generated analysis.)*"
        )
