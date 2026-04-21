"""
Report Exporter
───────────────
Generates downloadable outputs:
  • Full HTML report  (styled, self-contained)
  • Metrics CSV       (per-platform numbers)
  • Agent log CSV     (pipeline audit trail)
"""

import io
import pandas as pd
from datetime import datetime


# ── HTML Report ───────────────────────────────────────────────────────────────
def build_html_report(metrics: dict, decision: dict, finance: dict,
                       insight: str, logger_df: pd.DataFrame) -> str:
    winner   = decision["winner"]
    ranked   = decision["ranking"]
    fin      = finance
    now      = datetime.now().strftime("%d %B %Y, %H:%M")

    platforms_html = ""
    medals = ["🥇", "🥈", "🥉"] + [""] * 10
    for i, (p, score) in enumerate(ranked):
        m = metrics[p]
        highlight = "background:#eef4ff;border-left:4px solid #4f8ef7;" if p == winner else ""
        platforms_html += f"""
        <tr style="{highlight}">
            <td>{medals[i]} {p}</td>
            <td>₹{m['avg_revenue']:,.0f}</td>
            <td>{m['conversion_rate']:.2f}%</td>
            <td>₹{m['total_revenue']:,.0f}</td>
            <td>{m['total_users']}</td>
            <td><b>{score:.3f}</b></td>
        </tr>"""

    log_rows = ""
    for _, row in logger_df.iterrows():
        status_color = "#28a745" if row["status"] == "done" else "#f0a500"
        log_rows += f"""
        <tr>
            <td>{row['agent']}</td>
            <td style="color:{status_color};font-weight:600">{row['status'].upper()}</td>
            <td>{row['started_at']}</td>
            <td>{row['ended_at']}</td>
            <td>{row['duration_s']}s</td>
            <td style="font-size:12px;color:#555">{row['summary']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Business Decision Report — {now}</title>
<style>
  body  {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
  h1    {{ color: #1a1a2e; }}
  h2    {{ color: #4f8ef7; border-bottom: 2px solid #e0e0e0; padding-bottom: 6px; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 28px; }}
  th    {{ background: #f0f4ff; padding: 10px; text-align: left; font-size: 13px; }}
  td    {{ padding: 9px 10px; border-bottom: 1px solid #eee; font-size: 13px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin: 20px 0; }}
  .kpi  {{ background: #f8f9fa; border-radius: 8px; padding: 16px; text-align: center; }}
  .kpi .label {{ font-size: 12px; color: #777; }}
  .kpi .value {{ font-size: 24px; font-weight: 700; color: #1a1a2e; }}
  .winner-kpi {{ background: #eef4ff; border: 2px solid #4f8ef7; }}
  .insight-box {{ background: #f0f7ff; border-left: 4px solid #4f8ef7;
                  border-radius: 6px; padding: 18px 22px; line-height: 1.8;
                  font-size: 14px; color: #1a1a2e; }}
  .footer {{ color: #aaa; font-size: 11px; margin-top: 40px; text-align: center; }}
</style>
</head>
<body>
<h1>🤖 Multi-Agent Business Decision Report</h1>
<p style="color:#777">Generated: {now} &nbsp;|&nbsp; Powered by Grok LLM</p>

<h2>📈 Key Performance Indicators</h2>
<div class="kpi-grid">
  <div class="kpi winner-kpi">
    <div class="label">Best Platform</div>
    <div class="value">🏆 {winner}</div>
  </div>
  <div class="kpi">
    <div class="label">Highest Avg Revenue</div>
    <div class="value">₹{metrics[winner]['avg_revenue']:,.0f}</div>
  </div>
  <div class="kpi">
    <div class="label">Revenue Uplift</div>
    <div class="value">+{fin['uplift_pct']:.1f}%</div>
  </div>
  <div class="kpi">
    <div class="label">Projected Gain</div>
    <div class="value">₹{fin['improvement']:,.0f}</div>
  </div>
</div>

<h2>📊 Platform Comparison</h2>
<table>
  <tr>
    <th>Platform</th><th>Avg Revenue</th><th>Conversion</th>
    <th>Total Revenue</th><th>Users</th><th>Composite Score</th>
  </tr>
  {platforms_html}
</table>

<h2>💰 Financial Projections</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Current total revenue</td><td>₹{fin['current_total']:,.0f}</td></tr>
  <tr><td>Projected revenue (if all match {winner})</td><td>₹{fin['projected_total']:,.0f}</td></tr>
  <tr><td>Improvement opportunity</td><td style="color:#28a745;font-weight:700">₹{fin['improvement']:,.0f}</td></tr>
  <tr><td>Worst performer ({fin['worst_platform']})</td><td>₹{fin['worst_avg_rev']:,.0f} avg</td></tr>
  <tr><td>Revenue uplift</td><td style="color:#4f8ef7;font-weight:700">+{fin['uplift_pct']:.1f}%</td></tr>
</table>

<h2>🤖 AI-Generated Insight (Grok LLM)</h2>
<div class="insight-box">{insight.replace(chr(10), "<br>")}</div>

<h2>⚙️ Agent Execution Log</h2>
<table>
  <tr><th>Agent</th><th>Status</th><th>Started</th><th>Ended</th><th>Duration</th><th>Summary</th></tr>
  {log_rows}
</table>

<div class="footer">Multi-Agent Business Decision Support System &nbsp;·&nbsp; Grok xAI</div>
</body>
</html>"""


# ── Metrics CSV ───────────────────────────────────────────────────────────────
def build_metrics_csv(metrics: dict, decision: dict, finance: dict) -> bytes:
    rows = []
    for p, m in metrics.items():
        rows.append({
            "Platform":        p,
            "Avg Revenue (₹)": m["avg_revenue"],
            "Total Revenue":   m["total_revenue"],
            "Conversion Rate": m["conversion_rate"],
            "Total Users":     m["total_users"],
            "Composite Score": round(decision["scores"].get(p, 0), 4),
            "Rank":            next(i+1 for i, (pl,_) in enumerate(decision["ranking"]) if pl == p),
            "Winner":          "✓" if p == decision["winner"] else "",
        })
    df = pd.DataFrame(rows).sort_values("Rank")
    return df.to_csv(index=False).encode()
