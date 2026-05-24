# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL DEPLOY SAFE + LIGHT UI + PM INTEGRATED
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime
from paths import MODEL_PATH, FEATURE_PATH, DATA_PATH, POWERBI_PATH

# =========================================
# CONFIG (LIGHT SCADA UI)
# =========================================
st.set_page_config(page_title="Wire Bond SCADA Digital Twin", layout="wide")

st.markdown("""
<style>
.digital-twin {
    font-size: 22px;
    font-weight: bold;
    color: #2c7be5;
    animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {opacity: 1;}
  50% {opacity: 0.5;}
  100% {opacity: 1;}
}

.block {
    background-color: #f7f9fc;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #d6e4ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="digital-twin">🧠 Digital Twin Engine ACTIVE</div>', unsafe_allow_html=True)

# =========================================
# SAFE LOAD
# =========================================
if not MODEL_PATH.exists() or not DATA_PATH.exists() or not FEATURE_PATH.exists():
    st.error("Missing required files")
    st.stop()

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

# =========================================
# MACHINE FIX
# =========================================
if "Machine" not in df.columns:
    df["Machine"] = "WBO001"

df = df[df["Machine"].isin(["WBO001", "WBO002", "WBO003"])]

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("SCADA Control")

machine_id = st.sidebar.selectbox("Machine", ["WBO001", "WBO002", "WBO003"])

page = st.sidebar.radio(
    "Module",
    ["📊 KPI Dashboard", "🧪 Simulation Engine", "📡 Power BI Feed"]
)

# Refresh system
if st.sidebar.button("🔄 Refresh System"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# KPI DASHBOARD + PM SCHEDULER (INTEGRATED)
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard")

    avg_wear = machine_df["Capillary_Wear"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    avg_temp = machine_df["Bond_Head_Temperature"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    availability = max(0, 1 - avg_wear / 300)
    performance = min(1, avg_speed / 3000)
    quality = max(0, 1 - failure_rate / 100)

    oee = availability * performance * quality * 100
    risk = min(avg_wear / 300, 1)

    # =========================================
    # PM SCHEDULER (INTEGRATED RULE-BASED)
    # =========================================
    if avg_wear < 100:
        pm_status = "🟢 Normal - Next PM: 14 days"
    elif avg_wear < 200:
        pm_status = "🟠 Warning - Next PM: 7 days"
    else:
        pm_status = "🔴 Critical - Immediate PM Required"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{availability:.2f}")
    col2.metric("Performance", f"{performance:.2f}")
    col3.metric("Quality", f"{quality:.2f}")
    col4.metric("OEE", f"{oee:.2f}%")

    st.markdown(f"### Maintenance Status: {pm_status}")

    st.metric("Temperature", f"{avg_temp:.2f}")
    st.metric("Wear", f"{avg_wear:.2f}")
    st.metric("Failure %", f"{failure_rate:.2f}%")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 30], "color": "#d4f4dd"},
                {"range": [30, 70], "color": "#ffeaa7"},
                {"range": [70, 100], "color": "#ff7675"},
            ]
        }
    )))

# =========================================
# 🧪 SIMULATION ENGINE (STATIC PRESCRIPTIVE + RCA)
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine (Static Prescriptive Model)")

    st.sidebar.subheader("Simulation Inputs")

    bond_temp = st.sidebar.slider("Bond Temp", 290, 330, 310)
    speed = st.sidebar.slider("Speed", 1000, 3000, 1500)
    force = st.sidebar.slider("Force", 10, 100, 50)
    wear = st.sidebar.slider("Wear", 0, 300, 100)

    sim_df = pd.DataFrame([{
        "Bond_Head_Temperature": bond_temp,
        "Bonding_Speed": speed,
        "Bonding_Force": force,
        "Capillary_Wear": wear
    }])

    X = sim_df.reindex(columns=features, fill_value=0)
    prob = model.predict_proba(X)[0][1]

    # =========================================
    # ROOT CAUSE ANALYSIS (RULE BASED)
    # =========================================
    if wear > 200:
        root_cause = "Capillary Wear Degradation"
    elif bond_temp > 320:
        root_cause = "Thermal Overstress"
    elif speed < 1200:
        root_cause = "Low Bonding Throughput"
    else:
        root_cause = "Normal Variation"

    # =========================================
    # PRESCRIPTIVE ACTION (STATIC)
    # =========================================
    if prob > 0.7:
        action = "Replace capillary + shutdown inspection"
        status = "🔴 HIGH RISK"
    elif prob > 0.3:
        action = "Schedule maintenance within 7 days"
        status = "🟠 MEDIUM RISK"
    else:
        action = "Continue operation"
        status = "🟢 LOW RISK"

    st.markdown(f"### Risk Status: {status}")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 30], "color": "#d4f4dd"},
                {"range": [30, 70], "color": "#ffeaa7"},
                {"range": [70, 100], "color": "#ff7675"},
            ]
        }
    )))

    st.markdown("### Root Cause Analysis")
    st.info(root_cause)

    st.markdown("### Prescriptive Action")
    st.warning(action)

# =========================================
# 📡 POWER BI FEED (ENHANCED MULTI CHART)
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed (SCADA Export Layer)")

    if st.button("🔄 Refresh Power BI"):
        st.rerun()

    power_df = df.copy()

    power_df["Risk"] = power_df["Capillary_Wear"] / 300

    power_df["OEE"] = (
        (1 - power_df["Capillary_Wear"] / 300) *
        (power_df["Bonding_Speed"] / 3000) *
        (1 - power_df["Wirebond_Failure"])
    ) * 100

    power_df["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(power_df),
        freq="h"
    )

    st.metric("Avg OEE", f"{power_df['OEE'].mean():.2f}%")

    # =========================================
    # ENHANCED POWER BI VISUALS
    # =========================================

    st.plotly_chart(px.line(power_df, x="Timestamp", y="Bond_Head_Temperature", color="Machine"))
    st.plotly_chart(px.line(power_df, x="Timestamp", y="Capillary_Wear", color="Machine"))
    st.plotly_chart(px.line(power_df, x="Timestamp", y="OEE", color="Machine"))

    st.plotly_chart(px.bar(power_df, x="Machine", y="OEE"))

    st.plotly_chart(px.scatter(power_df, x="Capillary_Wear", y="OEE", color="Machine"))

    # Risk distribution
    st.plotly_chart(px.histogram(power_df, x="Risk", nbins=20))

    power_df.to_csv(POWERBI_PATH, index=False)

    st.success("📁 Power BI Export Updated")