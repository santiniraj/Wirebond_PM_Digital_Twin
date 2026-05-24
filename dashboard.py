# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL DEPLOY SAFE VERSION (NO FEATURE REMOVED)
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from paths import MODEL_PATH, FEATURE_PATH, DATA_PATH, POWERBI_PATH

# =========================================
# CONFIG
# =========================================
st.set_page_config(page_title="Wire Bond SCADA Digital Twin", layout="wide")

# =========================================
# HEADER
# =========================================
st.markdown("""
<style>
.digital-twin {
    font-size: 22px;
    font-weight: bold;
    color: #00ff99;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% {opacity: 1;}
  50% {opacity: 0.4;}
  100% {opacity: 1;}
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
# MACHINE FIX (IMPORTANT)
# =========================================
if "Machine" not in df.columns:
    if "Type" in df.columns:
        df["Machine"] = df["Type"].map({0: "WBO001", 1: "WBO002", 2: "WBO003"})
    else:
        df["Machine"] = "WBO001"

df["Machine"] = df["Machine"].fillna("WBO001")
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

machine_df = df[df["Machine"] == machine_id]

# =========================================
# KPI DASHBOARD (UNCHANGED LOGIC)
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard")

    avg_temp = machine_df["Bond_Head_Temperature"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    avg_force = machine_df["Bonding_Force"].mean()
    avg_wear = machine_df["Capillary_Wear"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    hist_risk = min(avg_wear / 300, 1)

    availability = 1 - (avg_wear / 300)
    performance = avg_speed / 3000
    quality = 1 - (failure_rate / 100)
    oee = availability * performance * quality * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{availability:.2f}")
    col2.metric("Performance", f"{performance:.2f}")
    col3.metric("Quality", f"{quality:.2f}")
    col4.metric("OEE %", f"{oee:.2f}%")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Temp", f"{avg_temp:.2f}")
    c2.metric("Speed", f"{avg_speed:.0f}")
    c3.metric("Force", f"{avg_force:.2f}")
    c4.metric("Wear", f"{avg_wear:.2f}")
    c5.metric("Failure %", f"{failure_rate:.2f}%")

    st.subheader("Machine Health")
    st.success("GOOD" if hist_risk < 0.3 else "WARNING" if hist_risk < 0.7 else "CRITICAL")

    rul = max(1, (300 - avg_wear) / 20)
    st.metric("RUL (Days)", f"{rul:.1f}")

    st.metric("Anomaly", f"{machine_df['Capillary_Wear'].std():.2f}")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=hist_risk * 100,
        gauge={"axis": {"range": [0, 100]}}
    )), use_container_width=True)

# =========================================
# SIMULATION ENGINE
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine")

    bond_temp = st.slider("Bond Temp", 290, 330, 310)
    heater_temp = st.slider("Heater Temp", 300, 360, 320)
    speed = st.slider("Speed", 1000, 3000, 1500)
    force = st.slider("Force", 10, 100, 50)
    wear = st.slider("Wear", 0, 300, 100)

    sim_df = pd.DataFrame([{
        "Bond_Head_Temperature": bond_temp,
        "Heater_Block_Temperature": heater_temp,
        "Bonding_Speed": speed,
        "Bonding_Force": force,
        "Capillary_Wear": wear
    }])

    X = sim_df.reindex(columns=features, fill_value=0)
    prob = model.predict_proba(X)[0][1]

    st.subheader("Risk Gauge")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red" if prob > 0.7 else "orange" if prob > 0.3 else "green"}
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recommendation")

    st.info("High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.3 else "Low Risk")

# =========================================
# POWER BI FEED
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed")

    power_df = df.copy()

    power_df["Risk"] = power_df["Capillary_Wear"] / 300

    power_df["OEE"] = (
        (1 - power_df["Capillary_Wear"]/300) *
        (power_df["Bonding_Speed"]/3000) *
        (1 - power_df["Wirebond_Failure"])
    ) * 100

    power_df["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(power_df),
        freq="H"
    )

    st.metric("Avg OEE", f"{power_df['OEE'].mean():.2f}%")

    st.plotly_chart(px.line(power_df, x="Timestamp", y="Bond_Head_Temperature", color="Machine"))
    st.plotly_chart(px.bar(power_df, x="Machine", y="OEE"))
    st.plotly_chart(px.scatter(power_df, x="Capillary_Wear", y="OEE"))

    power_df.to_csv(POWERBI_PATH, index=False)

    st.success("Export completed")