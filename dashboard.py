# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL FIXED VERSION (NO FEATURE REMOVED)
# MULTI-MACHINE + HIL + PM + RCA + PRIORITY
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="digital-twin">🧠 Digital Twin Engine ACTIVE</div>', unsafe_allow_html=True)

# =========================================
# LOAD DATA
# =========================================
if not MODEL_PATH.exists() or not DATA_PATH.exists() or not FEATURE_PATH.exists():
    st.error("Missing required files")
    st.stop()

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

# =========================================
# MACHINE VALIDATION (FIXED - NO LOSS OF WBO002/003)
# =========================================
if "Machine" not in df.columns:
    df["Machine"] = np.random.choice(["WBO001", "WBO002", "WBO003"], len(df))

df = df[df["Machine"].isin(["WBO001", "WBO002", "WBO003"])]

df_all = df.copy()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("SCADA Control")

machine_id = st.sidebar.selectbox("Machine", ["WBO001", "WBO002", "WBO003"])

page = st.sidebar.radio(
    "Module",
    ["📊 KPI Dashboard", "🧪 Simulation Engine", "📡 Power BI Feed"]
)

if st.sidebar.button("🔄 Refresh System"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# KPI DASHBOARD (WITH RISK GAUGE RESTORED)
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard (Multi-Machine SCADA View)")

    avg_wear = machine_df["Capillary_Wear"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    avg_temp = machine_df["Bond_Head_Temperature"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    availability = max(0, 1 - avg_wear / 300)
    performance = min(1, avg_speed / 3000)
    quality = max(0, 1 - failure_rate / 100)

    oee = availability * performance * quality * 100
    risk = min(avg_wear / 300, 1)

    # =========================
    # KPI COLORS
    # =========================
    def color(v):
        return "🟢" if v > 0.7 else "🟠" if v > 0.3 else "🔴"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{color(availability)} {availability:.2f}")
    col2.metric("Performance", f"{color(performance)} {performance:.2f}")
    col3.metric("Quality", f"{color(quality)} {quality:.2f}")
    col4.metric("OEE", f"{oee:.2f}%")

    # =========================
    # 🔴 RISK GAUGE (FIXED)
    # =========================
    st.subheader("Risk Gauge")

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

    # =========================
    # PM SCHEDULER (DETAILED)
    # =========================
    if avg_wear < 100:
        pm = "🟢 PM: Routine Inspection (14 days)"
        pm_detail = "Lubrication + visual capillary check"
    elif avg_wear < 200:
        pm = "🟠 PM: Preventive Action (7 days)"
        pm_detail = "Capillary inspection + bonding force calibration"
    else:
        pm = "🔴 PM: Immediate Shutdown Required"
        pm_detail = "Replace capillary + full head inspection + recalibration"

    st.subheader("Maintenance Plan")
    st.info(pm)
    st.write(pm_detail)

    st.metric("Temperature", f"{avg_temp:.2f}")
    st.metric("Wear", f"{avg_wear:.2f}")
    st.metric("Failure %", f"{failure_rate:.2f}%")

# =========================================
# 🧪 SIMULATION ENGINE (HIL + RCA RESTORED)
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine (HIL + Prescriptive System)")

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

    # =========================
    # ROOT CAUSE (REAL-TIME RULE ENGINE)
    # =========================
    if wear > 200:
        root_cause = "Capillary Wear Failure Dominant"
    elif bond_temp > 320:
        root_cause = "Thermal Stress Instability"
    elif speed < 1200:
        root_cause = "Low Bond Energy Transfer"
    else:
        root_cause = "System Stable"

    # =========================
    # PRESCRIPTIVE ACTION
    # =========================
    if prob > 0.7:
        action = "Immediate shutdown + capillary replacement"
        status = "🔴 HIGH RISK"
        hil = "HIL RELAY: TRIGGERED (STOP MACHINE)"
    elif prob > 0.3:
        action = "Schedule PM within 7 days"
        status = "🟠 MEDIUM RISK"
        hil = "HIL RELAY: WARNING MODE"
    else:
        action = "Continue operation"
        status = "🟢 LOW RISK"
        hil = "HIL RELAY: NORMAL OPERATION"

    st.markdown(f"### Risk Status: {status}")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 30], "color": "#d4f4dd"},
                {"range": [30, 70], "color": "#ffeaa7"},
                {"range": [70, 100], "color": "#ff7675"},
            ]
        }
    )))

    st.subheader("Root Cause Analysis")
    st.info(root_cause)

    st.subheader("Prescriptive Action")
    st.warning(action)

    st.subheader("HIL Decision Layer")
    st.code(hil)

# =========================================
# 📡 POWER BI FEED (WITH PRIORITY ENGINE FIXED)
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed (Multi-Machine Analytics + Priority)")

    if st.button("🔄 Refresh"):
        st.rerun()

    df_all["Risk"] = df_all["Capillary_Wear"] / 300

    df_all["OEE"] = (
        (1 - df_all["Capillary_Wear"] / 300) *
        (df_all["Bonding_Speed"] / 3000) *
        (1 - df_all["Wirebond_Failure"])
    ) * 100

    df_all["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(df_all),
        freq="h"
    )

    # =========================
    # MACHINE PRIORITY (NEW IMPORTANT FIX)
    # =========================
    priority = df_all.groupby("Machine")[["Risk", "OEE"]].mean()
    priority["Priority Score"] = priority["Risk"] * (100 - priority["OEE"])

    priority = priority.sort_values("Priority Score", ascending=False)

    st.subheader("🚨 PM Priority Ranking")
    st.dataframe(priority)

    st.subheader("📈 OEE Trend")
    st.plotly_chart(px.line(df_all, x="Timestamp", y="OEE", color="Machine"))

    st.subheader("📊 Wear Distribution")
    st.plotly_chart(px.histogram(df_all, x="Capillary_Wear", color="Machine"))

    st.subheader("🔥 KPI Heatmap")
    heat = df_all.groupby("Machine")[["Capillary_Wear", "OEE", "Bonding_Speed"]].mean()
    st.plotly_chart(px.imshow(heat, text_auto=True, aspect="auto"))

    st.subheader("📊 OEE Components")
    oee_breakdown = df_all.groupby("Machine").mean(numeric_only=True).reset_index()

    st.plotly_chart(px.bar(
        oee_breakdown,
        x="Machine",
        y=["Capillary_Wear", "Bonding_Speed", "Wirebond_Failure"],
        barmode="group"
    ))

    st.subheader("🧁 Risk Share")
    risk_sum = df_all.groupby("Machine")["Risk"].mean().reset_index()
    st.plotly_chart(px.pie(risk_sum, names="Machine", values="Risk"))

    df_all.to_csv(POWERBI_PATH, index=False)

    st.success("Power BI Export Updated")