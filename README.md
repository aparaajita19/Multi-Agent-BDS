# 🤖 Multi-Agent Business Decision Support System

An AI-powered e-commerce intelligence platform that extends A/B testing to
multi-platform comparison (Amazon · Meesho · Flipkart · Myntra) using a
**4-agent pipeline** powered by **Grok (xAI) LLM**.

---

## 📁 Project Structure

```
multi_agent_bds/
│
├── app.py                      ← Streamlit dashboard (entry point)
│
├── agents/
│   ├── __init__.py
│   ├── analyst_agent.py        ← Agent 1: computes revenue & conversion
│   ├── decision_agent.py       ← Agent 2: scores & ranks platforms
│   ├── finance_agent.py        ← Agent 3: revenue uplift prediction
│   └── insight_agent.py        ← Agent 4: Grok LLM explanation
│
├── utils/
│   ├── __init__.py
│   └── data_loader.py          ← CSV/Excel loader + sample data generator
│
├── data/
│   └── sample_data.csv         ← 30-row demo dataset
│
├── .streamlit/
│   └── secrets.toml            ← API key storage (never commit)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Step-by-Step Build Guide

### STEP 1 — Prerequisites

Make sure you have **Python 3.11+** installed.

```bash
python --version     # should be 3.11 or higher
```

Install pip if missing:
```bash
python -m ensurepip --upgrade
```

---

### STEP 2 — Create the Project Folder

```bash
mkdir multi_agent_bds
cd multi_agent_bds
mkdir agents utils data .streamlit
```

---

### STEP 3 — Set Up a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

---

### STEP 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package     | Purpose                                  |
|-------------|------------------------------------------|
| streamlit   | Web dashboard UI                         |
| pandas      | Data processing (Analyst Agent)          |
| plotly      | Interactive charts                       |
| openai      | Grok API client (OpenAI-compatible)      |
| openpyxl    | Excel file support                       |

---

### STEP 5 — Get Your Grok API Key

1. Go to → https://console.x.ai
2. Sign in with your X (Twitter) account
3. Click **"API Keys"** in the left sidebar
4. Click **"Create API Key"**
5. Copy the key (starts with `xai-...`)

> 💡 Grok uses the **OpenAI-compatible** API format, so the `openai` Python
> package works out of the box — just change the `base_url`.

---

### STEP 6 — Configure API Key (Two Options)

**Option A — In the UI** (easiest for testing):
Just paste the key in the sidebar when you run the app.

**Option B — In secrets.toml** (recommended for development):
```toml
# .streamlit/secrets.toml
GROK_API_KEY = "xai-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Then read it in `insight_agent.py`:
```python
import streamlit as st
api_key = st.secrets.get("GROK_API_KEY", "")
```

---

### STEP 7 — Copy All Source Files

Copy each file from this project into the matching path shown in the
project structure above. Every file is provided — no additional coding needed.

---

### STEP 8 — Run the App

```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

### STEP 9 — Use the Dashboard

1. **Sidebar** → paste your Grok API key
2. **Data Source** → use sample data OR upload your own CSV/Excel
3. **Platform Filter** → select which platforms to compare
4. Click **🚀 Run All Agents**
5. Watch all 4 agents execute sequentially
6. Review KPIs, charts, rankings, and AI insight

---

### STEP 10 — Upload Your Own Data

Your CSV/Excel must have these columns:

| Column    | Type    | Description                        |
|-----------|---------|------------------------------------|
| USER_ID   | int/str | Unique user identifier             |
| PLATFORM  | string  | Amazon / Meesho / Flipkart / Myntra|
| REVENUE   | float   | Revenue per transaction (₹)        |
| CONVERTED | int     | Optional: 1=converted, 0=not       |

Example:
```
USER_ID,PLATFORM,REVENUE,CONVERTED
1001,Amazon,1520,0
1002,Meesho,620,1
1003,Flipkart,1100,0
```

---

## 🤖 How the Agents Work

```
CSV/Excel Data
      │
      ▼
┌─────────────────┐
│  Analyst Agent  │  ← Pandas: avg revenue, conversion rate per platform
└────────┬────────┘
         │ metrics dict
         ▼
┌─────────────────┐
│ Decision Agent  │  ← Scoring: revenue×0.6 + conversion×0.4 → winner
└────────┬────────┘
         │ winner + ranking
         ▼
┌─────────────────┐
│  Finance Agent  │  ← Uplift %, projected revenue improvement
└────────┬────────┘
         │ financial projections
         ▼
┌─────────────────┐
│  Insight Agent  │  ← Grok LLM → human-readable business insight
└─────────────────┘
```

---

## ⚙️ Grok API — Key Details

```python
from openai import OpenAI

client = OpenAI(
    api_key="xai-your-key-here",
    base_url="https://api.x.ai/v1",   # ← only change from OpenAI
)

response = client.chat.completions.create(
    model="grok-3-mini",              # or "grok-3" for best quality
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.4,
    max_tokens=512,
)
print(response.choices[0].message.content)
```

Available Grok models:
| Model        | Speed  | Quality | Best for              |
|--------------|--------|---------|------------------------|
| grok-3-mini  | Fast   | Good    | Quick insights (cheap) |
| grok-3       | Slower | Best    | Detailed analysis      |

---

## 🔧 Customisation

**Change scoring weights** in `agents/decision_agent.py`:
```python
REVENUE_WEIGHT    = 0.60   # increase to weight revenue more
CONVERSION_WEIGHT = 0.40   # increase to weight conversion more
```

**Add more platforms** in `utils/data_loader.py`:
```python
PLATFORM_PARAMS = {
    "Amazon":   {...},
    "Nykaa":    {"rev_mu": 800, "rev_sd": 200, "conv": 0.078},  # new!
    ...
}
```

**Change Grok model** in `agents/insight_agent.py`:
```python
MODEL = "grok-3"   # switch from grok-3-mini to full model
```

---

## ❓ Troubleshooting

| Problem                  | Fix                                                   |
|--------------------------|-------------------------------------------------------|
| `ModuleNotFoundError`    | Run `pip install -r requirements.txt`                 |
| Grok API 401 error       | Check API key starts with `xai-` and is active        |
| Empty charts             | Ensure uploaded CSV has correct column names          |
| Port 8501 in use         | Run `streamlit run app.py --server.port 8502`         |
| `openai` import error    | Run `pip install openai>=1.30.0`                      |

---

## 📦 Deploy to Streamlit Cloud (Free)

1. Push to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to → https://share.streamlit.io
3. Connect your GitHub repo
4. Set `app.py` as the main file
5. In **Secrets**, add:
   ```
   GROK_API_KEY = "xai-xxxx"
   ```
6. Click Deploy ✅

---

## 📄 License

MIT — free to use and modify for personal or commercial projects.
