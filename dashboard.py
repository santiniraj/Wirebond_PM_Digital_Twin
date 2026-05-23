# =========================================
# 🏭 WIRE BOND INDUSTRY 4.0 DIGITAL TWIN
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Wire Bond Digital Twin",
    layout="wide"
)

# =========================
# BASE PATH (STREAMLIT SAFE)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "features.json")
DATA_PATH = os.path.join(BASE_DIR, "cleaned_wirebond_data.csv")

# =========================
# UI STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f4f7fb 0%, #ffffff 100%);
    font-family: Arial;
}

h1 {
    font-size: 42px !important;
    font-weight: 800;
    color: #1f3b57;
}

h2 {
    font-size: 28px !important;
}

div[data-testid="metric-container"] {
    font-size: 18px !important;
    padding: 14px !important;
}

.panel {
    background: rgba(255,255,255,0.9);
    padding: 16px;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.light-box {
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    font-size: 22px;
    font-weight: 800;
}

.green {background:#d4f8e8; color:#1e7e34;}
.orange {background:#fff3cd; color:#b26a00;}
.red {background:#f8d7da; color:#a10000;}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD MODEL + FEATURES
# =========================
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_resource
def load_features():
    with open(FEATURE_PATH, "r") as f:
        return json.load(f)

model = load_model()
features = load_features()

df = pd.read_csv(DATA_PATH)

# =========================
# TITLE
# =========================
st.title("🏭 Wire Bond Digital Twin – Industry 4.0 SCADA System")
st.markdown("Predictive Maintenance | AI Risk Monitoring | Smart Factory Dashboard")

# =========================
# REFRESH BUTTON
# =========================
if st.button("🔄 Refresh Dashboard"):
    st.rerun()

# =========================
# MACHINE ID (REAL INDUSTRY STYLE)
# =========================
machine_id = st.selectbox(
    "Select Machine ID",
    ["WBO001", "WBO002", "WBO003", "WBO004", "WBO005"]
)

# =========================
# SIDEBAR SENSORS
# =========================
st.sidebar.header("📡 Sensor Inputs")

bond_head = st.sidebar.slider("Bond Head Temp", 290, 330, 310)
heater = st.sidebar.slider("Heater Temp", 300, 360, 320)
speed = st.sidebar.slider("Bond Speed", 1000, 3000, 1500)
force = st.sidebar.slider("Bond Force", 10, 100, 50)
wear = st.sidebar.slider("Capillary Wear", 0, 300, 100)

# =========================
# FEATURE ENGINEERING
# =========================
input_df = pd.DataFrame([{
    "Bond_Head_Temperature": bond_head,
    "Heater_Block_Temperature": heater,
    "Bonding_Speed": speed,
    "Bonding_Force": force,
    "Capillary_Wear": wear
}])

input_df["Temperature_Difference"] = heater - bond_head
input_df["Force_Speed_Ratio"] = force / speed if speed != 0 else 0
input_df["Stress_Index"] = force * speed
input_df["Wear_Interaction"] = wear * (heater - bond_head)

X = input_df.reindex(columns=features, fill_value=0)

# =========================
# PREDICTION
# =========================
prob = model.predict_proba(X)[0][1]

# =========================
# RISK LOGIC
# =========================
if prob < 0.3:
    status = "SAFE"
    color = "green"
    label = "🟢 HEALTHY"
elif prob < 0.7:
    status = "WARNING"
    color = "orange"
    label = "🟡 WARNING"
else:
    status = "CRITICAL"
    color = "red"
    label = "🔴 CRITICAL"

# =========================
# HEADER KPI
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("Machine ID", machine_id)
c2.metric("Failure Risk", f"{prob:.2%}")
c3.metric("System Status", status)

# =========================
# TRAFFIC LIGHT DISPLAY
# =========================
st.markdown("## 🚦 Risk Status")

st.markdown(f"""
<div class="light-box {color}">
{label}<br>
Risk Score: {prob:.2%}
</div>
""", unsafe_allow_html=True)

# =========================
# GAUGE VISUALIZATION
# =========================
st.subheader("📊 Risk Gauge")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=prob * 100,
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
# AI EXPLANATION
# =========================
st.subheader("🧠 AI Insight")

if prob < 0.3:
    st.success("Machine operating normally. No action required.")
elif prob < 0.7:
    st.warning("Degradation detected in thermal or force system.")
else:
    st.error("High failure risk. Immediate maintenance required.")

# =========================
# MAINTENANCE SCHEDULER
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

st.dataframe(pd.DataFrame({
    "Machine": [machine_id],
    "Recommended Maintenance (Days)": [days],
    "Priority": [priority]
}))

# =========================
# DATA VIEW
# =========================
st.subheader("📦 Factory Dataset")
st.dataframe(df.head())