"""
Data Loader
───────────
Handles CSV / Excel uploads and generates synthetic sample data.

Expected columns (user-uploaded):
  USER_ID  | PLATFORM  | REVENUE  | CONVERTED (optional)
"""

import io
import random
import pandas as pd


# ── Upload loader ──────────────────────────────────────────────────────────────
def load_data(file) -> pd.DataFrame:
    """Load a CSV or Excel file uploaded via Streamlit."""
    name = file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type. Please upload CSV or Excel.")

    df.columns = [c.strip().upper() for c in df.columns]

    required = {"USER_ID", "PLATFORM", "REVENUE"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["PLATFORM"] = df["PLATFORM"].str.strip().str.title()
    df["REVENUE"]  = pd.to_numeric(df["REVENUE"], errors="coerce").fillna(0)
    return df


# ── Sample data generator ─────────────────────────────────────────────────────
PLATFORM_PARAMS = {
    "Amazon":   {"rev_mu": 1420, "rev_sd": 380, "conv": 0.072},
    "Meesho":   {"rev_mu":  680, "rev_sd": 210, "conv": 0.091},
    "Flipkart": {"rev_mu": 1180, "rev_sd": 310, "conv": 0.065},
    "Myntra":   {"rev_mu":  960, "rev_sd": 270, "conv": 0.083},
}


def generate_sample_data(n_per_platform: int = 60, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic e-commerce data for demo purposes."""
    random.seed(seed)
    rows = []
    uid  = 1001

    for platform, p in PLATFORM_PARAMS.items():
        for _ in range(n_per_platform):
            revenue   = max(50, random.gauss(p["rev_mu"], p["rev_sd"]))
            converted = 1 if random.random() < p["conv"] else 0
            rows.append({
                "USER_ID":   uid,
                "PLATFORM":  platform,
                "REVENUE":   round(revenue, 2),
                "CONVERTED": converted,
            })
            uid += 1

    return pd.DataFrame(rows)
