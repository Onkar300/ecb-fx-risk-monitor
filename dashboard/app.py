"""Phase 5 — ECB Macro & FX Risk Monitor (Streamlit dashboard).

Four views: Macro Overview, Volatility Monitor, Anomaly Detector, VaR Summary.
Reads from the analytics_marts tables built by dbt (Phase 3) and the risk
metrics build (Phase 4).

Run from the project root:
    streamlit run dashboard/app.py
"""
from __future__ import annotations

import os
import sys

# Make `src` importable when Streamlit runs this file directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import DB_URL
from sqlalchemy import create_engine, text

# --------------------------------------------------------------------------- #
# Page config + theme
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="ECB Macro & FX Risk Monitor",
    page_icon="\U0001F4C9",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette — refined dark "risk terminal".
BG = "#0d1117"
PANEL = "#161b22"
GRID = "#21262d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#e8a33d"      # amber
ACCENT2 = "#2f81f7"     # blue
DANGER = "#f85149"      # red (anomalies)
OK = "#3fb950"          # green

PAIR_COLORS = {
    "EUR_USD": "#2f81f7",
    "EUR_GBP": "#3fb950",
    "EUR_JPY": "#e8a33d",
    "EUR_CHF": "#db61a2",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif; }}
.stApp {{ background: {BG}; color: {TEXT}; }}
section[data-testid="stSidebar"] {{ background: {PANEL}; border-right: 1px solid {GRID}; }}

h1, h2, h3 {{ font-family: 'IBM Plex Sans', sans-serif; letter-spacing: -0.02em; }}
.app-title {{ font-size: 1.9rem; font-weight: 700; color: {TEXT}; margin-bottom: 0; }}
.app-sub {{ color: {MUTED}; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;
            letter-spacing: 0.08em; text-transform: uppercase; }}

/* Metric cards */
div[data-testid="stMetric"] {{
    background: {PANEL}; border: 1px solid {GRID}; border-radius: 10px;
    padding: 16px 18px;
}}
div[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; }}
div[data-testid="stMetricValue"] {{ font-family: 'IBM Plex Mono', monospace; color: {TEXT}; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{ background: {PANEL}; border: 1px solid {GRID};
    border-radius: 8px 8px 0 0; color: {MUTED}; font-weight: 500; }}
.stTabs [aria-selected="true"] {{ background: {BG}; color: {ACCENT};
    border-bottom: 2px solid {ACCENT}; }}

hr {{ border-color: {GRID}; }}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Data access
# --------------------------------------------------------------------------- #
@st.cache_resource
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)


@st.cache_data(ttl=600)
def load(query: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(query), conn)


def fmt_pct(x: float, dp: int = 2) -> str:
    return "n/a" if pd.isna(x) else f"{x*100:.{dp}f}%"


def base_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT, size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


PAIR_LABELS = {"EUR_USD": "EUR/USD", "EUR_GBP": "EUR/GBP",
               "EUR_JPY": "EUR/JPY", "EUR_CHF": "EUR/CHF"}
PAIR_COL = {"EUR_USD": "eur_usd", "EUR_GBP": "eur_gbp",
            "EUR_JPY": "eur_jpy", "EUR_CHF": "eur_chf"}


# --------------------------------------------------------------------------- #
# Header + sidebar
# --------------------------------------------------------------------------- #
st.markdown('<p class="app-title">ECB Macro &amp; FX Risk Monitor</p>', unsafe_allow_html=True)
st.markdown('<p class="app-sub">European Central Bank \u00b7 euro-area FX, policy rates &amp; inflation</p>',
            unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Controls")
    pair = st.selectbox("Currency pair", list(PAIR_LABELS),
                        format_func=lambda p: PAIR_LABELS[p])
    macro = load("select * from analytics_marts.fct_macro_snapshot order by obs_date")
    macro["obs_date"] = pd.to_datetime(macro["obs_date"])
    min_d, max_d = macro["obs_date"].min(), macro["obs_date"].max()
    date_range = st.date_input("Date range", value=(min_d, max_d),
                               min_value=min_d, max_value=max_d)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.caption("Data: ECB Data Portal API \u2192 PostgreSQL \u2192 dbt \u2192 risk metrics")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = min_d, max_d

mask = (macro["obs_date"] >= start) & (macro["obs_date"] <= end)
macro_f = macro[mask]

metrics = load("select * from analytics_marts.fct_fx_risk_metrics")
metrics["obs_date"] = pd.to_datetime(metrics["obs_date"])
m_pair = metrics[(metrics["pair"] == pair) &
                 (metrics["obs_date"] >= start) & (metrics["obs_date"] <= end)]

var = load("select * from analytics_marts.fct_fx_var_summary")


# --------------------------------------------------------------------------- #
# KPI row
# --------------------------------------------------------------------------- #
latest = macro_f.dropna(subset=[PAIR_COL[pair]]).iloc[-1] if not macro_f.empty else None
latest_vol = m_pair.dropna(subset=["rolling_vol_21d"])
v_row = var[var["pair"] == pair].iloc[0] if not var.empty else None

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{PAIR_LABELS[pair]} (latest)",
          f"{latest[PAIR_COL[pair]]:.4f}" if latest is not None else "n/a")
c2.metric("Rolling vol (21d, ann.)",
          fmt_pct(latest_vol["rolling_vol_21d"].iloc[-1]) if not latest_vol.empty else "n/a")
c3.metric("VaR 95% (1-day, hist.)",
          fmt_pct(v_row["historical_var_95"]) if v_row is not None else "n/a")
c4.metric("Anomalies in range", int(m_pair["is_anomaly"].sum()))

st.markdown("<hr/>", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
t1, t2, t3, t4 = st.tabs(["Macro Overview", "Volatility Monitor",
                          "Anomaly Detector", "VaR Summary"])

# --- Macro Overview ---
with t1:
    st.subheader("FX rates, ECB policy rates & inflation")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=macro_f["obs_date"], y=macro_f[PAIR_COL[pair]],
                             name=PAIR_LABELS[pair], line=dict(color=PAIR_COLORS[pair], width=2)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=macro_f["obs_date"], y=macro_f["dfr_rate"],
                             name="ECB Deposit Rate", line=dict(color=ACCENT, width=1.5, dash="dot")),
                  secondary_y=True)
    fig.update_yaxes(title_text=PAIR_LABELS[pair], secondary_y=False)
    fig.update_yaxes(title_text="Policy rate (%)", secondary_y=True)
    st.plotly_chart(base_layout(fig), use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=macro_f["obs_date"], y=macro_f["hicp_yoy_pct"],
                              name="HICP inflation (YoY %)", line=dict(color=DANGER, width=2),
                              fill="tozeroy", fillcolor="rgba(248,81,73,0.08)"))
    fig2.add_hline(y=2.0, line_dash="dash", line_color=MUTED,
                   annotation_text="ECB 2% target", annotation_font_color=MUTED)
    st.plotly_chart(base_layout(fig2, 320), use_container_width=True)

# --- Volatility Monitor ---
with t2:
    st.subheader(f"{PAIR_LABELS[pair]} \u2014 realised vs GARCH conditional volatility")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m_pair["obs_date"], y=m_pair["rolling_vol_21d"],
                             name="21-day realised (ann.)", line=dict(color=ACCENT2, width=2)))
    fig.add_trace(go.Scatter(x=m_pair["obs_date"], y=m_pair["garch_cond_vol"],
                             name="GARCH(1,1) conditional (ann.)", line=dict(color=ACCENT, width=1.6)))
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(base_layout(fig), use_container_width=True)
    st.caption("Realised vol = rolling sample stdev \u00d7 \u221a252. GARCH captures "
               "volatility clustering. Agreement between the two is a sanity check; "
               "GARCH reacts faster to shocks.")

# --- Anomaly Detector ---
with t3:
    st.subheader(f"{PAIR_LABELS[pair]} \u2014 daily returns & flagged anomalies")
    normal = m_pair[~m_pair["is_anomaly"]]
    anom = m_pair[m_pair["is_anomaly"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=normal["obs_date"], y=normal["log_return"],
                             mode="markers", name="Daily return",
                             marker=dict(color=MUTED, size=3, opacity=0.5)))
    fig.add_trace(go.Scatter(x=anom["obs_date"], y=anom["log_return"],
                             mode="markers", name="Anomaly (|z|>3)",
                             marker=dict(color=DANGER, size=8, symbol="x")))
    fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(base_layout(fig), use_container_width=True)
    st.markdown(f"**{len(anom)} anomalies** flagged in the selected range "
                f"(rolling 60-day z-score beyond \u00b13).")
    if not anom.empty:
        show = anom[["obs_date", "log_return", "zscore_60d"]].copy()
        show["obs_date"] = show["obs_date"].dt.date
        show["log_return"] = (show["log_return"] * 100).round(2).astype(str) + "%"
        show["zscore_60d"] = show["zscore_60d"].round(2)
        show.columns = ["Date", "Return", "Z-score"]
        st.dataframe(show.sort_values("Date", ascending=False),
                     use_container_width=True, hide_index=True, height=260)

# --- VaR Summary ---
with t4:
    st.subheader("Value-at-Risk \u2014 historical vs parametric")
    disp = var.copy()
    disp["pair"] = disp["pair"].map(PAIR_LABELS)
    for col in ["historical_var_95", "parametric_var_95",
                "historical_var_99", "parametric_var_99"]:
        disp[col] = (disp[col] * 100).round(3).astype(str) + "%"
    disp = disp[["pair", "historical_var_95", "parametric_var_95",
                 "historical_var_99", "parametric_var_99", "n_observations"]]
    disp.columns = ["Pair", "Hist VaR 95%", "Param VaR 95%",
                    "Hist VaR 99%", "Param VaR 99%", "Obs"]
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.caption("One-day VaR as a positive loss magnitude. Historical = empirical "
               "quantile (no distributional assumption). Parametric = normal "
               "approximation. Divergence in the 99% tail reflects fat tails in FX returns.")
