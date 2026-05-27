# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, timedelta
import pytz

from paths import MODEL_PATH, FEATURE_PATH, DATA_PATH, POWERBI_PATH

# =========================================
# CONFIG
# =========================================
st.set_page_config(page_title="SCADA Digital Twin", layout="wide")

# =========================================
# TIME FIX (Malaysia)
# =========================================
local_tz = pytz.timezone("Asia/Kuala_Lumpur")
current_time = datetime.now(local_tz)

st.sidebar.markdown("### ⏱ System Timestamp")
st.sidebar.success(current_time.strftime("%Y-%m-%d %H:%M:%S"))

st.markdown("""
<style>
.digital {font-size:22px;font-weight:bold;color:#2b6cb0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="digital">🧠 SCADA DIGITAL TWIN ACTIVE</div>', unsafe_allow_html=True)

# =========================================
# LOAD DATA
# =========================================
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

if "Machine" not in df.columns:
    df["Machine"] = np.random.choice(["WBO001","WBO002","WBO003"], len(df))

df = df[df["Machine"].isin(["WBO001","WBO002","WBO003"])]
df_all = df.copy()

# =========================================
# HIL LOG
# =========================================
HIL_FILE = "hil_log.csv"

try:
    hil_log = pd.read_csv(HIL_FILE)
except:
    hil_log = pd.DataFrame(columns=["Time","Machine","Risk","System_Action","Operator_Decision"])

def log_hil(machine, risk, system_action, operator):
    global hil_log
    new = pd.DataFrame([{
        "Time": datetime.now(),
        "Machine": machine,
        "Risk": risk,
        "System_Action": system_action,
        "Operator_Decision": operator
    }])
    hil_log = pd.concat([hil_log, new], ignore_index=True)
    hil_log.to_csv(HIL_FILE, index=False)

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("Control Panel")
machine_id = st.sidebar.selectbox("Machine", ["WBO001","WBO002","WBO003"])

page = st.sidebar.radio(
    "Module",
    ["📊 Performance Dashboard", "🧪 Simulation Engine", "📡 Analytics Feed"]
)

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# COLOR ENGINE (UNCHANGED LOGIC)
# =========================================
def risk_color(v):
    if v < 0.3:
        return "#1B5E20"
    elif v < 0.7:
        return "#E65100"
    return "#B71C1C"

# =========================================
# AI ENGINE
# =========================================
def ai_diagnosis(wear, temp, speed):
    if wear > 200:
        return "Capillary degradation detected", "Immediate inspection required"
    elif temp > 320:
        return "Thermal instability detected", "Reduce heater load"
    elif speed < 1200:
        return "Low production efficiency", "Adjust bonding speed"
    else:
        return "System stable", "Continue operation"

# =========================================
# PM SCHEDULER
# =========================================
def pm_schedule(wear):
    today = datetime.today()
    if wear < 100:
        return "Routine Maintenance", today + timedelta(days=14)
    elif wear < 200:
        return "Preventive Maintenance", today + timedelta(days=7)
    else:
        return "Urgent Maintenance", today + timedelta(days=1)

# =========================================
# 📊 PERFORMANCE DASHBOARD
# =========================================
if page == "📊 Performance Dashboard":

    st.title("📊 Machine Performance Dashboard")

    wear = machine_df["Capillary_Wear"].mean()
    speed = machine_df["Bonding_Speed"].mean()
    temp = machine_df["Bond_Head_Temperature"].mean()
    fail = machine_df["Wirebond_Failure"].mean()

    availability = 1 - wear/300
    performance = speed/3000
    quality = 1 - fail
    oee = availability * performance * quality * 100
    risk = wear/300

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{availability:.2f}")
    col2.metric("Performance", f"{performance:.2f}")
    col3.metric("Quality", f"{quality:.2f}")
    col4.metric("OEE %", f"{oee:.2f}")

    st.subheader("Risk Gauge")

    # ===========================
    # FIXED GAUGE (YELLOW VALUE)
    # ===========================
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk*100,

        number={
            "font": {"size": 45, "color": "yellow"},  # ⭐ YELLOW VALUE FIX
            "suffix": "%"
        },

        gauge={
            "axis": {"range": [0, 100]},

            "bar": {
                "color": "yellow",   # ⭐ FORCE YELLOW INDICATOR
                "thickness": 0.3
            },

            "steps": [
                {"range": [0, 30], "color": "#2ECC71"},
                {"range": [30, 70], "color": "#F39C12"},
                {"range": [70, 100], "color": "#E74C3C"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    issue, action = ai_diagnosis(wear,temp,speed)
    pm_type, pm_date = pm_schedule(wear)

    st.info(issue)
    st.warning(action)
    st.success(f"{pm_type} | {pm_date.strftime('%Y-%m-%d')}")

    st.subheader("Operator Decision History")
    st.dataframe(hil_log[hil_log["Machine"] == machine_id])

# =========================================
# 🧪 SIMULATION ENGINE
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine")

    temp = st.sidebar.slider("Temperature",290,330,310)
    speed = st.sidebar.slider("Speed",1000,3000,1500)
    force = st.sidebar.slider("Force",10,100,50)
    wear = st.sidebar.slider("Wear",0,300,100)

    sim = pd.DataFrame([{
        "Bond_Head_Temperature": temp,
        "Bonding_Speed": speed,
        "Bonding_Force": force,
        "Capillary_Wear": wear
    }])

    X = sim.reindex(columns=features, fill_value=0)
    prob = model.predict_proba(X)[0][1]
    risk = prob

    st.subheader("Simulation Risk Gauge")

    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk*100,

        number={
            "font": {"size": 45, "color": "yellow"},
            "suffix": "%"
        },

        gauge={
            "axis": {"range": [0, 100]},

            "bar": {
                "color": "yellow",
                "thickness": 0.3
            },

            "steps": [
                {"range": [0, 30], "color": "#2ECC71"},
                {"range": [30, 70], "color": "#F39C12"},
                {"range": [70, 100], "color": "#E74C3C"}
            ]
        }
    ))

    st.plotly_chart(fig2, use_container_width=True)

    issue, action = ai_diagnosis(wear,temp,speed)
    pm_type, pm_date = pm_schedule(wear)

    st.info(issue)
    st.warning(action)
    st.success(f"{pm_type} | {pm_date.strftime('%Y-%m-%d')}")

    system_action = "Approve Maintenance" if risk > 0.5 else "Continue Operation"
    operator = st.radio("Operator Decision",["Approve","Reject","Override"])

    if st.button("Confirm HIL Decision"):
        log_hil(machine_id, risk, system_action, operator)
        st.success("Decision Logged")

    st.subheader("Operator Decision History")
    st.dataframe(hil_log[hil_log["Machine"] == machine_id])

# =========================================
# 📡 POWER BI ANALYTICS FEED
# =========================================
if page == "📡 PowerBI Analytics Feed":

    st.title("📡 PowerBI Analytics Feed")

    df_all["Availability"] = 1 - df_all["Capillary_Wear"]/300
    df_all["Performance"] = df_all["Bonding_Speed"]/3000
    df_all["Quality"] = 1 - df_all["Wirebond_Failure"]

    df_all["Efficiency"] = df_all["Availability"] * df_all["Performance"] * df_all["Quality"] * 100
    df_all["Risk"] = df_all["Capillary_Wear"]/300

    df_all["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(df_all),
        freq="h"
    )

    priority = df_all.groupby("Machine")[["Risk","Efficiency"]].mean()
    priority["Priority Score"] = priority["Risk"]*(100-priority["Efficiency"])
    priority = priority.sort_values("Priority Score", ascending=False)

    st.subheader("Maintenance Priority")
    st.dataframe(priority)

    st.subheader("Efficiency Trend")
    st.plotly_chart(px.line(df_all, x="Timestamp", y="Efficiency", color="Machine"))

    st.subheader("Risk Distribution")
    st.plotly_chart(px.histogram(df_all, x="Risk", color="Machine"))

    st.subheader("Heatmap")
    heat = df_all.groupby("Machine")[["Risk","Efficiency"]].mean()
    st.plotly_chart(px.imshow(heat, text_auto=True))

    st.subheader("Component Breakdown")
    st.plotly_chart(px.bar(df_all, x="Machine", y=["Availability","Performance","Quality"], barmode="group"))

    df_all.to_csv(POWERBI_PATH, index=False)
    st.success("Power BI Dataset Export Completed")