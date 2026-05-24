# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# DISTINCTION VERSION (FULL RESTORED + ENHANCED)
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# =========================================
# CONFIG
# =========================================
st.set_page_config(
    page_title="Wire Bond SCADA Digital Twin",
    layout="wide"
)

# =========================================
# DIGITAL TWIN ANIMATION (CORRECT PLACE = TOP UI LAYER)
# =========================================
st.markdown("""
<style>
@keyframes pulse {
  0% {opacity: 1;}
  50% {opacity: 0.4;}
  100% {opacity: 1;}
}
.digital-twin {
    animation: pulse 1.5s infinite;
    font-size: 22px;
    font-weight: bold;
    color: #00ff99;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="digital-twin">🧠 Digital Twin Engine ACTIVE</div>',
    unsafe_allow_html=True
)

# =========================================
# LOAD DATA + MODEL (CLEAN VERSION)
# =========================================

import streamlit as st
import joblib
import json
import pandas as pd

from paths import MODEL_PATH, FEATURE_PATH, CLEANED_DATA_PATH

model = joblib.load(MODEL_PATH)

df = pd.read_csv(CLEANED_DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

# =========================
# DEBUG PATHS (OPTIONAL)
# =========================
st.write("MODEL PATH:", MODEL_PATH)
st.write("DATA PATH:", CLEANED_DATA_PATH)

# =========================
# VALIDATION
# =========================
if not MODEL_PATH.exists():
    st.error("❌ model.pkl not found")
    st.stop()

if not CLEANED_DATA_PATH.exists():
    st.error("❌ cleaned_wirebond_data.csv not found")
    st.stop()

if not FEATURE_PATH.exists():
    st.error("❌ features.json not found")
    st.stop()

# =========================
# LOAD MODEL
# =========================
model = joblib.load(MODEL_PATH)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(CLEANED_DATA_PATH)

# =========================
# LOAD FEATURES
# =========================
with open(FEATURE_PATH, "r") as f:
    features = json.load(f)
# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("🏭 SCADA CONTROL PANEL")

machine_id = st.sidebar.selectbox("Select Machine", ["WBO001", "WBO002", "WBO003"])

page = st.sidebar.radio(
    "Select Module",
    ["📊 KPI Dashboard", "🧪 Simulation Engine", "📡 Power BI Feed"]
)
# =========================
# MACHINE COLUMN FIX
# =========================

MACHINE_MAP = {0: "WBO001", 1: "WBO002", 2: "WBO003"}

if "Machine" in df.columns:
    df["Machine"] = df["Machine"].fillna("WBO001")

elif "Type" in df.columns:
    df["Machine"] = df["Type"].map(MACHINE_MAP)

else:
    df["Machine"] = "WBO001"

df = df[df["Machine"].isin(["WBO001", "WBO002", "WBO003"])]

machine_df = df[df["Machine"] == machine_id].copy()

# =========================================================
# 🟢 KPI DASHBOARD (RESTORED FULL INTELLIGENCE)
# =========================================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard")

    if st.button("🔄 Refresh KPI"):
        st.rerun()

    avg_temp = machine_df["Bond_Head_Temperature"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    avg_force = machine_df["Bonding_Force"].mean()
    avg_wear = machine_df["Capillary_Wear"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    hist_risk = min(avg_wear / 300, 1)

    # ================================
    # ⚙️ OEE CALCULATION (FIXED POSITION)
    # ================================
    availability = 1 - (avg_wear / 300)
    performance = avg_speed / 3000
    quality = 1 - (failure_rate / 100)

    oee = availability * performance * quality * 100

    st.subheader("⚙ Overall Equipment Effectiveness (OEE)")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Availability", f"{availability:.2f}")
    col2.metric("Performance", f"{performance:.2f}")
    col3.metric("Quality", f"{quality:.2f}")
    col4.metric("OEE %", f"{oee:.2f}%")

    # ================================
    # KPI ROW
    # ================================
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Temp", f"{avg_temp:.2f}")
    c2.metric("Speed", f"{avg_speed:.0f}")
    c3.metric("Force", f"{avg_force:.2f}")
    c4.metric("Wear", f"{avg_wear:.2f}")
    c5.metric("Failure %", f"{failure_rate:.2f}%")

    # ================= HEALTH =================
    st.subheader("🏭 Machine Health")
    st.success(
        "🟢 GOOD" if hist_risk < 0.3
        else "🟠 WARNING" if hist_risk < 0.7
        else "🔴 CRITICAL"
    )

    # ================= RUL =================
    rul = max(1, (300 - avg_wear) / 20)
    st.metric("📅 RUL (Days)", f"{rul:.1f}")

    # ================= ANOMALY =================
    anomaly_score = machine_df["Capillary_Wear"].std()
    st.metric("🚨 Anomaly Indicator", f"{anomaly_score:.2f}")

    # ================= GAUGE =================
    st.subheader("📊 Risk Gauge")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=hist_risk * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 30], "color": "green"},
                {"range": [30, 70], "color": "orange"},
                {"range": [70, 100], "color": "red"}
            ]
        }
    )), use_container_width=True)

    # ================= 🧠 AGENTIC AI =================
    st.subheader("🧠 Agentic AI Insight Engine")

    if hist_risk < 0.3:
        root = "Stable process with normal variation."
        action = "Continue monitoring"
        risk = "LOW"

    elif hist_risk < 0.7:
        root = "Wear accumulation detected in capillary system."
        action = "Schedule preventive maintenance"
        risk = "MEDIUM"

    else:
        root = "Critical degradation in bonding system."
        action = "Immediate intervention required"
        risk = "HIGH"

    st.success(f"Risk Level: {risk}")
    st.info(f"Root Cause: {root}")
    st.warning(f"Recommendation: {action}")

    # ================= 📅 PM SCHEDULER =================
    pm_days = 14 if hist_risk < 0.3 else 5 if hist_risk < 0.7 else 1

    st.subheader("📅 Maintenance Scheduler")

    st.warning(f"Next PM Due In: {pm_days} days")
    st.info(f"Suggested Date: {(datetime.now() + timedelta(days=pm_days)).date()}")
# =========================================================
# 🧪 SIMULATION ENGINE (FIXED + FULL RESTORED + PRESCRIPTIVE)
# =========================================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine")

    if st.button("🔄 Refresh Simulation"):
        st.rerun()

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

    # =====================================================
    # 📊 SIMULATION RISK GAUGE (FIXED INDENTATION)
    # =====================================================
    st.subheader("📊 Simulation Risk Gauge")

    color = "green" if prob < 0.3 else "orange" if prob < 0.7 else "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,

        number={
            "font": {
                "color": "black",
                "size": 40
            }
        },

        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "bgcolor": "white",

            "steps": [
                {"range": [0, 30], "color": "#d4f7d4"},
                {"range": [30, 70], "color": "#fff3cd"},
                {"range": [70, 100], "color": "#f8d7da"}
            ],

            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": prob * 100
            }
        }
    ))

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 🧠 PRESCRIPTIVE ENGINE
    # =====================================================
    st.subheader("🧠 Prescriptive AI Engine")

    if prob < 0.3:
        rec = "Maintain current parameters"
        action = "No intervention"

    elif prob < 0.7:
        rec = "Reduce speed 10–15%, monitor wear"
        action = "Optimize process"

    else:
        rec = "Stop machine immediately"
        action = "Critical intervention"

    st.success(f"Action: {action}")
    st.info(rec)

    # =====================================================
    # 📅 PM SCHEDULER
    # =====================================================
    pm_days = 14 if prob < 0.3 else 5 if prob < 0.7 else 1
    st.warning(f"Simulated PM in: {pm_days} days")

    # =====================================================
    # 👨 HIL (FULL RESTORED)
    # =====================================================
    st.subheader("👨 Human-in-the-Loop")

    decision = st.radio("Operator Decision", ["Select", "Approve PM", "Reject PM"])
    comment = st.text_input("Comment")

    if "hil_log" not in st.session_state:
        st.session_state.hil_log = []

    if decision != "Select":
        st.session_state.hil_log.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "decision": decision,
            "comment": comment
        })

    st.dataframe(pd.DataFrame(st.session_state.hil_log))

# =========================================================
# 📡 POWER BI FEED (ENHANCED + MORE CHARTS)
# =========================================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Analytics Center")

    if st.button("🔄 Refresh Power BI"):
        st.rerun()

    power_df = df.copy()

    power_df["Predicted_Risk"] = (power_df["Capillary_Wear"] / 300).clip(0, 1)

    power_df["Risk_Level"] = np.where(
        power_df["Predicted_Risk"] < 0.3, "LOW",
        np.where(power_df["Predicted_Risk"] < 0.7, "MEDIUM", "HIGH")
    )

    power_df["OEE"] = (
        (1 - power_df["Capillary_Wear"]/300) *
        (power_df["Bonding_Speed"]/3000) *
        (1 - power_df["Wirebond_Failure"])
    ) * 100

    power_df["Timestamp"] = pd.date_range(
        start=datetime.now() - timedelta(hours=len(power_df)),
        periods=len(power_df),
        freq="H"
    )

    # ================= KPI =================
    st.subheader("📊 Fleet KPI Overview")

    st.metric("Avg OEE", f"{power_df['OEE'].mean():.2f}%")
    st.metric("Avg Risk", f"{power_df['Predicted_Risk'].mean()*100:.2f}%")

    # ================= TREND ANALYTICS =================
    st.subheader("📈 Trend Analytics")

    st.plotly_chart(px.line(power_df, x="Timestamp", y="Bond_Head_Temperature", color="Machine"))
    st.plotly_chart(px.line(power_df, x="Timestamp", y="Bonding_Speed", color="Machine"))
    st.plotly_chart(px.line(power_df, x="Timestamp", y="Capillary_Wear", color="Machine"))

    # ================= OEE =================
    st.subheader("⚙ OEE Analysis")
    st.plotly_chart(px.bar(power_df, x="Machine", y="OEE", color="Risk_Level"))

    # ================= HEATMAP =================
    st.subheader("🔥 Risk Heatmap")
    heat = power_df.groupby(["Machine", "Risk_Level"]).size().reset_index(name="Count")
    st.plotly_chart(px.density_heatmap(heat, x="Machine", y="Risk_Level", z="Count"))

    # ================= SCATTER =================
    st.subheader("🔍 Correlation Analysis")
    st.plotly_chart(px.scatter(power_df, x="Capillary_Wear", y="OEE", color="Risk_Level"))

    # ================= FAILURE =================
    st.subheader("🚨 Failure Distribution")
    st.plotly_chart(px.pie(power_df, names="Risk_Level"))

    # ================= EXPORT =================
    export_path = os.path.join(BASE_DIR, "..", "powerbi_feed.csv")
    power_df.to_csv(export_path, index=False)

    st.success("Export completed")