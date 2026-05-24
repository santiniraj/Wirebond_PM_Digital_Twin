# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL DEPLOY SAFE VERSION (NO FEATURE REMOVED)
# ENHANCED VISUAL + PM + POWER BI FIX
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
# CONFIG
# =========================================
st.set_page_config(page_title="Wire Bond SCADA Digital Twin", layout="wide")

# =========================================
# HEADER STYLE (MORE INDUSTRIAL COLORS)
# =========================================
st.markdown("""
<style>
.digital-twin {
    font-size: 24px;
    font-weight: bold;
    color: #00ff99;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {opacity: 1;}
  50% {opacity: 0.3;}
  100% {opacity: 1;}
}

.kpi-box {
    padding: 10px;
    border-radius: 10px;
    background-color: #111;
    border: 1px solid #00ff99;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="digital-twin">🧠 Digital Twin Engine ACTIVE</div>', unsafe_allow_html=True)

# =========================================
# SAFE FILE LOADING
# =========================================
if not MODEL_PATH.exists():
    st.error(f"Missing model: {MODEL_PATH}")
    st.stop()

if not DATA_PATH.exists():
    st.error(f"Missing data: {DATA_PATH}")
    st.stop()

if not FEATURE_PATH.exists():
    st.error(f"Missing features: {FEATURE_PATH}")
    st.stop()

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

# =========================================
# MACHINE FIX
# =========================================
if "Machine" not in df.columns:
    if "Type" in df.columns:
        df["Machine"] = df["Type"].map({0: "WBO001", 1: "WBO002", 2: "WBO003"})
    else:
        df["Machine"] = "WBO001"

df["Machine"] = df["Machine"].fillna("WBO001")
df = df[df["Machine"].isin(["WBO001", "WBO002", "WBO003"])]

# =========================================
# SIDEBAR CONTROL
# =========================================
st.sidebar.title("🛠 SCADA Control")

machine_id = st.sidebar.selectbox("Machine", ["WBO001", "WBO002", "WBO003"])

page = st.sidebar.radio(
    "Module",
    ["📊 KPI Dashboard", "🧪 Simulation Engine", "📡 Power BI Feed", "📅 PM Scheduler"]
)

# =========================================
# 🔄 GLOBAL REFRESH BUTTON
# =========================================
if st.sidebar.button("🔄 REFRESH SYSTEM"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# KPI DASHBOARD
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard")

    avg_temp = machine_df["Bond_Head_Temperature"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    avg_force = machine_df["Bonding_Force"].mean()
    avg_wear = machine_df["Capillary_Wear"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    # OEE logic
    availability = max(0, 1 - (avg_wear / 300))
    performance = min(1, avg_speed / 3000)
    quality = max(0, 1 - (failure_rate / 100))
    oee = availability * performance * quality * 100

    # Risk
    risk = min(avg_wear / 300, 1)

    def risk_color(r):
        if r < 0.3:
            return "🟢 GOOD"
        elif r < 0.7:
            return "🟠 WARNING"
        else:
            return "🔴 CRITICAL"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{availability:.2f}")
    col2.metric("Performance", f"{performance:.2f}")
    col3.metric("Quality", f"{quality:.2f}")
    col4.metric("OEE %", f"{oee:.2f}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Temp", f"{avg_temp:.2f}")
    c2.metric("Speed", f"{avg_speed:.0f}")
    c3.metric("Force", f"{avg_force:.2f}")
    c4.metric("Wear", f"{avg_wear:.2f}")
    c5.metric("Failure %", f"{failure_rate:.2f}%")

    st.subheader("Machine Health Status")
    st.markdown(f"### {risk_color(risk)}")

    rul = max(1, (300 - avg_wear) / 20)
    st.metric("RUL (Days)", f"{rul:.1f}")

    st.metric("Anomaly Index", f"{machine_df['Capillary_Wear'].std():.2f}")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 30], "color": "green"},
                {"range": [30, 70], "color": "orange"},
                {"range": [70, 100], "color": "red"},
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

# =========================================
# 🧪 SIMULATION ENGINE (LEFT SIDEBAR CONTROL)
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine")

    st.sidebar.subheader("Simulation Controls")

    bond_temp = st.sidebar.slider("Bond Temp", 290, 330, 310)
    heater_temp = st.sidebar.slider("Heater Temp", 300, 360, 320)
    speed = st.sidebar.slider("Speed", 1000, 3000, 1500)
    force = st.sidebar.slider("Force", 10, 100, 50)
    wear = st.sidebar.slider("Wear", 0, 300, 100)

    sim_df = pd.DataFrame([{
        "Bond_Head_Temperature": bond_temp,
        "Heater_Block_Temperature": heater_temp,
        "Bonding_Speed": speed,
        "Bonding_Force": force,
        "Capillary_Wear": wear
    }])

    X = sim_df.reindex(columns=features, fill_value=0)
    prob = model.predict_proba(X)[0][1]

    def risk_color(prob):
        if prob < 0.3:
            return "🟢 LOW"
        elif prob < 0.7:
            return "🟠 MEDIUM"
        else:
            return "🔴 HIGH"

    st.subheader("Risk Gauge")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 30], "color": "green"},
                {"range": [30, 70], "color": "orange"},
                {"range": [70, 100], "color": "red"},
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk Level")
    st.markdown(f"### {risk_color(prob)}")

    st.subheader("Prescriptive Recommendation")

    if prob > 0.7:
        st.error("🔴 Immediate Maintenance Required")
        st.write("Action: Stop machine + replace capillary + inspect bonding head")
    elif prob > 0.3:
        st.warning("🟠 Schedule Maintenance Soon")
        st.write("Action: Inspect wear trend + reduce speed")
    else:
        st.success("🟢 Continue Operation")
        st.write("Action: Normal operation")

# =========================================
# 📡 POWER BI FEED (FIXED)
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed")

    if st.button("🔄 Refresh Power BI Feed"):
        st.rerun()

    power_df = df.copy()

    power_df["Risk"] = power_df["Capillary_Wear"] / 300

    power_df["OEE"] = (
        (1 - power_df["Capillary_Wear"] / 300) *
        (power_df["Bonding_Speed"] / 3000) *
        (1 - power_df["Wirebond_Failure"])
    ) * 100

    # ✅ FIXED SAFETY CHECK (inside block)
    if len(power_df) == 0:
        st.warning("No data available for Power BI feed")
        st.stop()

    power_df["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(power_df),
        freq="h"
    )

    st.metric("Avg OEE", f"{power_df['OEE'].mean():.2f}%")

    st.plotly_chart(
        px.line(power_df, x="Timestamp", y="Bond_Head_Temperature", color="Machine")
    )

    st.plotly_chart(
        px.bar(power_df, x="Machine", y="OEE")
    )

    st.plotly_chart(
        px.scatter(power_df, x="Capillary_Wear", y="OEE")
    )

    power_df.to_csv(POWERBI_PATH, index=False)

    st.success("📁 Power BI Export Completed")

# =========================================
# 📅 PM SCHEDULER (NEW BUT NON-DESTRUCTIVE ADDITION)
# =========================================
if page == "📅 PM Scheduler":

    st.title("📅 Preventive Maintenance Scheduler")

    avg_wear = machine_df["Capillary_Wear"].mean()

    if avg_wear < 100:
        next_pm = "In 14 Days"
        action = "Normal Monitoring"
    elif avg_wear < 200:
        next_pm = "In 7 Days"
        action = "Inspect Capillary"
    else:
        next_pm = "IMMEDIATE"
        action = "Replace Capillary + Bond Head Inspection"

    st.metric("Next PM Window", next_pm)

    st.warning(f"Recommended Action: {action}")

    st.write("Rule-based PM system (no AI):")
    st.code("""
    IF wear < 100 → PM in 14 days
    IF wear 100–200 → PM in 7 days
    IF wear > 200 → Immediate maintenance
    """)