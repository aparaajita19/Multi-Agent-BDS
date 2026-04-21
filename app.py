"""
Multi-Agent Business Decision Support System
════════════════════════════════════════════
Entry point — run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

from agents.analyst_agent  import AnalystAgent
from agents.decision_agent import DecisionAgent
from agents.finance_agent  import FinanceAgent
from agents.insight_agent  import InsightAgent

from utils.data_loader     import load_data
from utils.agent_logger    import AgentLogger
from utils.charts          import (revenue_bar, conversion_bar, radar_chart,
                                   revenue_box, finance_bar, user_pie)
from utils.report_exporter import build_html_report, build_metrics_csv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent BDS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.ag-card   { border:1.5px solid #dee2e6; border-radius:10px; padding:14px 12px;
             text-align:center; transition:border-color .3s; }
.ag-idle   { border-color:#dee2e6; }
.ag-running{ border-color:#f0a500; background:#fffbf0; }
.ag-done   { border-color:#28a745; background:#f0fff4; }
.insight-panel { background:linear-gradient(135deg,#eef4ff 0%,#f5f0ff 100%);
  border-left:5px solid #4f8ef7; border-radius:8px;
  padding:20px 24px; font-size:15px; line-height:1.85; color:#1a1a2e; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🤖 Multi-Agent BDS")
    st.caption("Business Decision Support System")
    st.divider()

    st.markdown("### 📂 Upload Data")
    uploaded_file = st.file_uploader(
        "Drop your CSV or Excel file here",
        type=["csv", "xlsx"],
        help="Required columns: USER_ID, PLATFORM, REVENUE. Optional: CONVERTED"
    )
    with st.expander("Expected column format"):
        st.code("USER_ID, PLATFORM, REVENUE, CONVERTED(optional)")

    st.divider()

    st.markdown("### 🛍️ Platform Filter")
    all_platforms = ["Amazon", "Meesho", "Flipkart", "Myntra"]
    selected = st.multiselect("Platforms", all_platforms, default=all_platforms,
                              label_visibility="collapsed")
    st.divider()

    st.markdown("### ⚖️ Scoring Weights")
    rev_w  = st.slider("Revenue weight", 0.0, 1.0, 0.60, 0.05)
    conv_w = round(1.0 - rev_w, 2)
    st.caption(f"Conversion weight auto-set to **{conv_w}**")
    st.divider()

    run_btn = st.button("🚀 Run All Agents", use_container_width=True,
                        type="primary",
                        disabled=(not selected or uploaded_file is None))
    if not uploaded_file:
        st.warning("Upload a CSV or Excel file to continue.", icon="📂")
    elif not selected:
        st.warning("Select at least one platform.")

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("🤖 Multi-Agent Business Decision Support System")
st.caption("A/B testing extended to multi-platform e-commerce · Amazon · Meesho · Flipkart · Myntra · Powered by Groq LLM")
st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.info("👈 Upload a CSV or Excel file from the sidebar to get started.", icon="📂")
    st.stop()

try:
    raw_df = load_data(uploaded_file)
    st.success(f"Loaded {len(raw_df)} rows from **{uploaded_file.name}**")
except Exception as e:
    st.error(f"Data error: {e}")
    st.stop()

df = raw_df[raw_df["PLATFORM"].isin(selected)] if selected else raw_df

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_main, tab_data, tab_log = st.tabs(["📊 Dashboard", "📋 Data Preview", "⚙️ Agent Log"])

with tab_data:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total rows",    len(df))
    c2.metric("Platforms",     df["PLATFORM"].nunique())
    c3.metric("Total revenue", f"₹{df['REVENUE'].sum():,.0f}")
    st.dataframe(df, use_container_width=True, height=420)
    st.download_button("⬇️ Download filtered CSV",
                       data=df.to_csv(index=False).encode(),
                       file_name="filtered_data.csv", mime="text/csv")

with tab_log:
    log_ph = st.empty()
    log_ph.info("Run the agents to see the execution log.")

# ── Agent status row ──────────────────────────────────────────────────────────
with tab_main:
    st.subheader("🤖 Agent Pipeline")
    ag_cols = st.columns(4)
    ag_status = {}
    agent_defs = [
        ("analyst",  "📊", "Analyst",       "Revenue & conversion metrics"),
        ("decision", "🧠", "Decision",      "Platform scoring & ranking"),
        ("finance",  "💰", "Finance",       "Revenue impact prediction"),
        ("insight",  "🤖", "Insight (LLM)", "Groq AI explanation"),
    ]
    for col, (key, *_) in zip(ag_cols, agent_defs):
        ag_status[key] = col.empty()

    def render_agents(states):
        for col, (key, icon, name, desc) in zip(ag_cols, agent_defs):
            state = states.get(key, "idle")
            cls   = f"ag-{state}"
            dot   = {"idle":"⬜","running":"🟡","done":"🟢"}[state]
            lbl   = {"idle":"Idle","running":"Running…","done":"Done ✓"}[state]
            ag_status[key].markdown(f"""
            <div class="ag-card {cls}">
                <div style="font-size:28px">{icon}</div>
                <div style="font-weight:600;font-size:14px;margin:4px 0">{name}</div>
                <div style="font-size:12px;color:#777">{desc}</div>
                <div style="margin-top:8px;font-size:13px">{dot} {lbl}</div>
            </div>""", unsafe_allow_html=True)

    render_agents({})
    st.divider()

    kpi_ph     = st.empty()
    charts_ph  = st.empty()
    radar_ph   = st.empty()
    fin_ph     = st.empty()
    insight_ph = st.empty()
    export_ph  = st.empty()

# ══════════════════════════════════════════════════════════════════════════════
# RUN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    if df.empty:
        st.error("No data for selected platforms.")
        st.stop()

    # Read Groq key from secrets (set in .streamlit/secrets.toml)
    groq_key = st.secrets.get("GROQ_API_KEY", "")

    logger = AgentLogger()
    states = {}

    # 1️⃣ Analyst
    states["analyst"] = "running"; render_agents(states); logger.start("Analyst")
    metrics = AnalystAgent(df).run()
    logger.done("Analyst", f"Processed {len(df)} rows / {len(metrics)} platforms")
    states["analyst"] = "done"; render_agents(states)

    # 2️⃣ Decision
    states["decision"] = "running"; render_agents(states); logger.start("Decision")
    decision = DecisionAgent(metrics, rev_weight=rev_w, conv_weight=conv_w).run()
    winner   = decision["winner"]
    logger.done("Decision", f"Winner: {winner} (score {decision['scores'][winner]:.3f})")
    states["decision"] = "done"; render_agents(states)

    # 3️⃣ Finance
    states["finance"] = "running"; render_agents(states); logger.start("Finance")
    finance = FinanceAgent(metrics, winner).run()
    logger.done("Finance", f"Uplift +{finance['uplift_pct']:.1f}% | Gain ₹{finance['improvement']:,.0f}")
    states["finance"] = "done"; render_agents(states)

    # 4️⃣ Insight (Groq)
    states["insight"] = "running"; render_agents(states); logger.start("Insight")
    insight_text = InsightAgent(metrics, decision, finance, api_key=groq_key).run()
    logger.done("Insight", "AI insight generated via Groq LLM")
    states["insight"] = "done"; render_agents(states)

    # ── Render results ────────────────────────────────────────────────────────
    with tab_main:

        # KPIs
        with kpi_ph.container():
            st.subheader("📈 Key Performance Indicators")
            k1,k2,k3,k4,k5 = st.columns(5)
            best_conv = max(metrics, key=lambda p: metrics[p]["conversion_rate"])
            k1.metric("🏆 Best Platform",  winner, f"Score {decision['scores'][winner]:.3f}")
            k2.metric("💰 Highest Avg Rev", f"₹{metrics[winner]['avg_revenue']:,.0f}", winner)
            k3.metric("🎯 Best Conv Rate",  f"{metrics[best_conv]['conversion_rate']:.1f}%", best_conv)
            k4.metric("📈 Revenue Uplift",  f"+{finance['uplift_pct']:.1f}%", f"vs {finance['worst_platform']}")
            k5.metric("💹 Projected Gain",  f"₹{finance['improvement']:,.0f}", "if all match winner")

        # Charts grid
        with charts_ph.container():
            st.subheader("📊 Platform Comparison")
            ch1,ch2 = st.columns(2)
            ch1.plotly_chart(revenue_bar(metrics),    use_container_width=True)
            ch2.plotly_chart(conversion_bar(metrics), use_container_width=True)
            ch3,ch4 = st.columns(2)
            ch3.plotly_chart(revenue_box(df),         use_container_width=True)
            ch4.plotly_chart(user_pie(metrics),       use_container_width=True)

        # Radar + ranking
        with radar_ph.container():
            st.subheader("🎯 Multi-Dimensional Analysis")
            r1,r2 = st.columns([1.1, 0.9])
            with r1:
                st.plotly_chart(radar_chart(metrics, decision["scores"]), use_container_width=True)
            with r2:
                st.markdown("**🏅 Composite Ranking**")
                st.caption(f"Revenue {rev_w:.0%} · Conversion {conv_w:.0%}")
                medals = ["🥇","🥈","🥉"] + ["  "]*10
                max_sc = decision["ranking"][0][1]
                for i,(plat,sc) in enumerate(decision["ranking"]):
                    pct = int(sc/max_sc*100)
                    mc,nc,bc,vc = st.columns([0.4,1.2,5,0.8])
                    mc.write(medals[i]); nc.write(f"**{plat}**")
                    bc.progress(pct);    vc.write(f"`{pct}`")

                rows = [{"Platform":p,
                         "Avg Rev":f"₹{m['avg_revenue']:,.0f}",
                         "Conv %":f"{m['conversion_rate']:.2f}%",
                         "Users":m["total_users"],
                         "Score":f"{decision['scores'].get(p,0):.3f}"}
                        for p,m in metrics.items()]
                st.dataframe(pd.DataFrame(rows).sort_values("Score",ascending=False),
                             use_container_width=True, hide_index=True)

        # Finance
        with fin_ph.container():
            st.subheader("💰 Financial Projections")
            fc1,fc2 = st.columns([1.2, 0.8])
            fc1.plotly_chart(finance_bar(finance), use_container_width=True)
            with fc2:
                st.markdown("**Projection breakdown**")
                st.markdown(f"""
| Metric | Value |
|--------|-------|
| Current total | ₹{finance['current_total']:,.0f} |
| Projected total | ₹{finance['projected_total']:,.0f} |
| **Improvement** | **₹{finance['improvement']:,.0f}** |
| Worst performer | {finance['worst_platform']} @ ₹{finance['worst_avg_rev']:,.0f} |
| Uplift | **+{finance['uplift_pct']:.1f}%** |
""")

        # Insight
        with insight_ph.container():
            st.subheader("🤖 AI-Generated Insight (Groq LLM)")
            st.markdown(
                f'<div class="insight-panel">{insight_text.replace(chr(10),"<br>")}</div>',
                unsafe_allow_html=True)

        # Export
        with export_ph.container():
            st.divider()
            st.subheader("⬇️ Export Results")
            ex1,ex2,ex3 = st.columns(3)
            log_df = logger.to_dataframe()
            ex1.download_button("📄 Full HTML Report",
                                data=build_html_report(metrics,decision,finance,insight_text,log_df).encode(),
                                file_name="bds_report.html", mime="text/html",
                                use_container_width=True)
            ex2.download_button("📊 Metrics CSV",
                                data=build_metrics_csv(metrics,decision,finance),
                                file_name="platform_metrics.csv", mime="text/csv",
                                use_container_width=True)
            ex3.download_button("⚙️ Agent Log CSV",
                                data=log_df.to_csv(index=False).encode(),
                                file_name="agent_log.csv", mime="text/csv",
                                use_container_width=True)

    # Agent log tab
    with tab_log:
        log_ph.empty()
        log_df = logger.to_dataframe()
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.caption(f"Total pipeline time: **{log_df['duration_s'].sum():.2f}s**")

    st.toast(f"✅ Done! Winner: **{winner}** · Uplift +{finance['uplift_pct']:.1f}%", icon="🏆")
