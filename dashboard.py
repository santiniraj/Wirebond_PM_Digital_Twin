# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL VERSION WITH HIL + TRACKING + OEE SPLIT
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
# LOAD DATA
# =========================================
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

with open(FEATURE_PATH) as f:
    features = json.load(f)

df_all = df.copy()

# =========================================
# HIL LOG STORAGE (NEW - TRACKING)
# =========================================
HIL_LOG_FILE = "hil_log.csv"

try:
    hil_log = pd.read_csv(HIL_LOG_FILE)
except:
    hil_log = pd.DataFrame(columns=[
        "Timestamp", "Machine", "Risk", "Decision", "Operator_Action"
    ])

def save_hil(machine, risk, decision, action):
    global hil_log
    new_row = pd.DataFrame([{
        "Timestamp": datetime.now(),
        "Machine": machine,
        "Risk": risk,
        "Decision": decision,
        "Operator_Action": action
    }])
    hil_log = pd.concat([hil_log, new_row], ignore_index=True)
    hil_log.to_csv(HIL_LOG_FILE, index=False)

# =========================================
# MACHINE SETUP (ALL 3 ENABLED)
# =========================================
if "Machine" not in df.columns:
    df["Machine"] = np.random.choice(["WBO001", "WBO002", "WBO003"], len(df))

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

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# KPI DASHBOARD (HIL STATUS ADDED)
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard (SCADA + HIL Tracking)")

    avg_wear = machine_df["Capillary_Wear"].mean()
    avg_speed = machine_df["Bonding_Speed"].mean()
    failure_rate = machine_df["Wirebond_Failure"].mean() * 100

    availability = max(0, 1 - avg_wear / 300)
    performance = min(1, avg_speed / 3000)
    quality = max(0, 1 - failure_rate / 100)
    oee = availability * performance * quality * 100

    risk = min(avg_wear / 300, 1)

    # =========================
    # KPI COLORS
    # =========================
    def c(v):
        return "🟢" if v > 0.7 else "🟠" if v > 0.3 else "🔴"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Availability", f"{c(availability)} {availability:.2f}")
    col2.metric("Performance", f"{c(performance)} {performance:.2f}")
    col3.metric("Quality", f"{c(quality)} {quality:.2f}")
    col4.metric("OEE", f"{oee:.2f}%")

    st.subheader("Risk Gauge")
    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk * 100,
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 30], "color": "#d4f4dd"},
                {"range": [30, 70], "color": "#ffeaa7"},
                {"range": [70, 100], "color": "#ff7675"},
            ]
        }
    )))

    # =========================
    # SHOW HIL HISTORY
    # =========================
    st.subheader("HIL Decision History")
    st.dataframe(hil_log[hil_log["Machine"] == machine_id])

# =========================================
# 🧪 SIMULATION ENGINE (HIL + HUMAN APPROVAL)
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine (HIL Controlled)")

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
    # RCA
    # =========================
    if wear > 200:
        root = "Capillary Wear Failure"
    elif bond_temp > 320:
        root = "Thermal Stress"
    else:
        root = "Normal"

    # =========================
    # HIL DECISION
    # =========================
    if prob > 0.7:
        decision = "RECOMMEND SHUTDOWN"
    elif prob > 0.3:
        decision = "SCHEDULE PM"
    else:
        decision = "CONTINUE"

    st.markdown(f"### Decision: {decision}")
    st.info(root)

    # =========================
    # HUMAN APPROVAL (NEW REQUIRED FEATURE)
    # =========================
    st.subheader("HIL Approval Required")

    action = st.radio(
        "Operator Decision",
        ["ACCEPT", "REJECT"]
    )

    if st.button("CONFIRM DECISION"):
        save_hil(machine_id, prob, decision, action)
        st.success("Decision Logged Successfully")

# =========================================
# 📡 POWER BI FEED (OEE SPLIT + COLORS FIXED)
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed (OEE + Multi Machine Analytics)")

    df_all["Risk"] = df_all["Capillary_Wear"] / 300

    df_all["Availability"] = 1 - df_all["Capillary_Wear"] / 300
    df_all["Performance"] = df_all["Bonding_Speed"] / 3000
    df_all["Quality"] = 1 - df_all["Wirebond_Failure"]

    df_all["OEE"] = df_all["Availability"] * df_all["Performance"] * df_all["Quality"] * 100

    df_all["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(df_all),
        freq="h"
    )

    # =========================
    # OEE COMPONENT VISUALS (FIXED REQUEST)
    # =========================
    st.subheader("📊 OEE Components (Correct Breakdown)")

    st.plotly_chart(px.bar(df_all, x="Machine", y="Availability", color="Machine"))
    st.plotly_chart(px.bar(df_all, x="Machine", y="Performance", color="Machine"))
    st.plotly_chart(px.bar(df_all, x="Machine", y="Quality", color="Machine"))

    # =========================
    # COLORS FIXED VISUALS
    # =========================
    st.plotly_chart(px.line(df_all, x="Timestamp", y="OEE", color="Machine"))

    st.plotly_chart(px.histogram(df_all, x="Risk", color="Machine"))

    st.plotly_chart(px.scatter(df_all, x="Capillary_Wear", y="OEE", color="Machine"))

    # =========================
    # SAVE FOR POWER BI
    # =========================
    df_all.to_csv(POWERBI_PATH, index=False)

    st.success("Power BI Export Updated with OEE Components")