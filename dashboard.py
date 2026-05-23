import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# =========================================
# 🏭 WIRE BOND INDUSTRY 4.0 DIGITAL TWIN
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
import plotly.graph_objects as go


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Wire Bond Smart Factory",
    layout="wide"
)

# =========================
# THEME (SCADA STYLE CLEAN UI)
# =========================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f4f7fb 0%, #ffffff 100%);
    font-family: Arial;
}

/* BIG TITLE */
h1 {
    font-size: 40px !important;
    font-weight: 800;
    color: #1f3b57;
}

/* SUB TITLE */
h2 {
    font-size: 30px !important;
}

/* METRICS */
div[data-testid="metric-container"] {
    font-size: 20px !important;
    padding: 16px !important;
}

/* PANEL */
.panel {
    background: rgba(255,255,255,0.9);
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

/* TRAFFIC LIGHT */
.light-box {
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    font-size: 26px;
    font-weight: 800;
}

/* COLORS */
.green {background:#d4f8e8; color:#1e7e34;}
.orange {background:#fff3cd; color:#b26a00;}
.red {background:#f8d7da; color:#a10000;}

</style>
""", unsafe_allow_html=True)

# =========================
# PATHS
# =========================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from paths import DATA_PATH, MODEL_PATH
from decision_engine import maintenance_decision

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_resource
def load_features():
    with open("models/trained/features.json") as f:
        return json.load(f)

model = load_model()
features = load_features()

df = pd.read_csv(DATA_PATH)

# =========================
# TITLE
# =========================
st.title("🏭 Wire Bond Smart Factory – Industry 4.0 Digital Twin")
st.markdown("Real-Time Predictive Maintenance | SCADA Monitoring | AI Decision System")

# =========================
# REFRESH BUTTON (MANUAL ONLY)
# =========================
if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# =========================
# MACHINE SELECTION
# =========================
machines = ["WBO001", "WBO002", "WBO003", "WBO004", "WBO005"]
machine = st.selectbox("Select Machine ID", machines)

# =========================
# INPUT SENSOR DATA
# =========================
st.sidebar.header("📡 Machine Sensors")

Bond_Head = st.sidebar.slider("Bond Head Temperature", 290, 330, 310)
Heater = st.sidebar.slider("Heater Temperature", 300, 360, 320)
Speed = st.sidebar.slider("Bond Speed", 1000, 3000, 1500)
Force = st.sidebar.slider("Bond Force", 10, 100, 50)
Wear = st.sidebar.slider("Capillary Wear", 0, 300, 100)

# =========================
# FEATURE ENGINEERING
# =========================
input_df = pd.DataFrame([{
    "Type": 1,
    "Bond_Head_Temperature": Bond_Head,
    "Heater_Block_Temperature": Heater,
    "Bonding_Speed": Speed,
    "Bonding_Force": Force,
    "Capillary_Wear": Wear
}])

input_df["Temperature_Difference"] = Heater - Bond_Head
input_df["Force_Speed_Ratio"] = Force / Speed if Speed != 0 else 0
input_df["Stress_Index"] = Force * Speed
input_df["Wear_Interaction"] = Wear * (Heater - Bond_Head)

X = input_df.reindex(columns=features, fill_value=0)

# =========================
# PREDICTION
# =========================
prob = model.predict_proba(X)[0][1]

risk, action = maintenance_decision(prob)

# =========================
# TRAFFIC LIGHT SYSTEM
# =========================
if prob < 0.3:
    status = "SAFE"
    color = "green"
    label = "🟢 SYSTEM HEALTHY"
elif prob < 0.7:
    status = "WARNING"
    color = "orange"
    label = "🟡 WARNING - MONITOR REQUIRED"
else:
    status = "CRITICAL"
    color = "red"
    label = "🔴 CRITICAL - IMMEDIATE ACTION"

# =========================
# HEADER KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Machine ID", machine)
c2.metric("Failure Risk", f"{prob:.2%}")
c3.metric("System Status", status)

# =========================
# 🚦 TRAFFIC LIGHT DISPLAY
# =========================
st.markdown("## 🚦 Risk Indicator (SCADA View)")

st.markdown(f"""
<div class="light-box {color}">
{label}<br><br>
Risk Score: {prob:.2%}
</div>
""", unsafe_allow_html=True)

# =========================
# 📊 RISK GAUGE
# =========================
st.subheader("📊 Risk Gauge")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=prob * 100,
    title={"text": "Failure Probability (%)"},
    gauge={
        "axis": {"range": [0, 100]},
        "steps": [
            {"range": [0, 30], "color": "#2ecc71"},
            {"range": [30, 70], "color": "#f39c12"},
            {"range": [70, 100], "color": "#e74c3c"}
        ],
        "bar": {"color": "black"}
    }
))

st.plotly_chart(fig, use_container_width=True)

# =========================
# 🧠 EXPLANATION (SIMPLE)
# =========================
st.subheader("🧠 AI Explanation")

if prob < 0.3:
    st.success("System operating normally with stable parameters.")
elif prob < 0.7:
    st.warning("Increasing stress detected in thermal or force systems.")
else:
    st.error("Critical imbalance detected. Immediate maintenance required.")

# =========================
# 📅 PREDICTIVE MAINTENANCE SCHEDULER
# =========================
st.subheader("📅 Maintenance Scheduler")

if prob < 0.3:
    days = 14
    priority = "LOW"
elif prob < 0.7:
    days = 5
    priority = "MEDIUM"
else:
    days = 1
    priority = "HIGH"

schedule_df = pd.DataFrame({
    "Machine": [machine],
    "Recommended Maintenance (Days)": [days],
    "Priority": [priority]
})

st.dataframe(schedule_df)

# =========================
# 📦 DATA VIEW
# =========================
st.subheader("📦 Factory Dataset")
st.dataframe(df.head())