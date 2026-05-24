# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# FULL INTEGRATED VERSION (STABLE + DEPLOY SAFE)
# KPI + SIMULATION + POWER BI + HIL + PM + EXPORT
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from paths import MODEL_PATH, FEATURE_PATH, DATA_PATH, POWERBI_PATH

# =========================================
# CONFIG
# =========================================
st.set_page_config(page_title="SCADA Digital Twin", layout="wide")

st.markdown("""
<style>
.digital {font-size:22px;font-weight:bold;color:#1f77b4;}
.good {color:green;}
.warn {color:orange;}
.bad {color:red;}
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

# Ensure machines exist
if "Machine" not in df.columns:
    df["Machine"] = np.random.choice(["WBO001", "WBO002", "WBO003"], len(df))

df = df[df["Machine"].isin(["WBO001", "WBO002", "WBO003"])]
df_all = df.copy()

# =========================================
# HIL LOG
# =========================================
HIL_FILE = "hil_log.csv"

try:
    hil_log = pd.read_csv(HIL_FILE)
except:
    hil_log = pd.DataFrame(columns=["Time","Machine","Risk","Decision","Action"])

def log_hil(machine, risk, decision, action):
    global hil_log
    new = pd.DataFrame([{
        "Time": datetime.now(),
        "Machine": machine,
        "Risk": risk,
        "Decision": decision,
        "Action": action
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
    ["📊 KPI Dashboard", "🧪 Simulation Engine", "📡 Power BI Feed"]
)

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

machine_df = df[df["Machine"] == machine_id]

# =========================================
# COMMON FUNCTIONS
# =========================================
def rca(wear,temp,speed):
    if wear>200: return "Capillary degradation"
    if temp>320: return "Thermal stress"
    if speed<1200: return "Low bonding efficiency"
    return "Stable"

def pm(wear):
    if wear<100: return "PM: 14 days"
    if wear<200: return "PM: 7 days"
    return "PM: Immediate"

# =========================================
# 📊 KPI DASHBOARD
# =========================================
if page == "📊 KPI Dashboard":

    st.title("📊 KPI Dashboard (Historical)")

    wear = machine_df["Capillary_Wear"].mean()
    speed = machine_df["Bonding_Speed"].mean()
    temp = machine_df["Bond_Head_Temperature"].mean()
    fail = machine_df["Wirebond_Failure"].mean()

    availability = 1 - wear/300
    performance = speed/3000
    quality = 1 - fail

    oee = availability*performance*quality*100
    risk = wear/300

    def color(v): return "🟢" if v>0.7 else "🟠" if v>0.3 else "🔴"

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Availability", f"{color(availability)} {availability:.2f}")
    col2.metric("Performance", f"{color(performance)} {performance:.2f}")
    col3.metric("Quality", f"{color(quality)} {quality:.2f}")
    col4.metric("OEE", f"{oee:.2f}%")

    st.subheader("Risk Gauge")
    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk*100,
        gauge={"axis":{"range":[0,100]}}
    )))

    st.subheader("PM + RCA")
    st.success(pm(wear))
    st.info(rca(wear,temp,speed))

    st.subheader("HIL History")
    st.dataframe(hil_log[hil_log["Machine"]==machine_id])

# =========================================
# 🧪 SIMULATION ENGINE
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation Engine (AI + HIL)")

    temp = st.sidebar.slider("Temp",290,330,310)
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

    st.subheader("Risk Gauge")
    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob*100,
        gauge={"axis":{"range":[0,100]}}
    )))

    st.info("RCA: " + rca(wear,temp,speed))
    st.warning("Action: " + ("Shutdown" if prob>0.7 else "PM required" if prob>0.3 else "Run"))

    st.success(pm(wear))

    st.subheader("HIL Decision")

    decision = "REJECT" if prob>0.5 else "ACCEPT"
    action = st.radio("Operator Decision",["ACCEPT","REJECT"])

    if st.button("Confirm HIL"):
        log_hil(machine_id, prob, decision, action)
        st.success("Logged")

# =========================================
# 📡 POWER BI FEED
# =========================================
if page == "📡 Power BI Feed":

    st.title("📡 Power BI Feed")

    df_all["Availability"] = 1 - df_all["Capillary_Wear"]/300
    df_all["Performance"] = df_all["Bonding_Speed"]/3000
    df_all["Quality"] = 1 - df_all["Wirebond_Failure"]

    df_all["OEE"] = df_all["Availability"]*df_all["Performance"]*df_all["Quality"]*100
    df_all["Risk"] = df_all["Capillary_Wear"]/300

    df_all["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(df_all),
        freq="h"
    )

    # PRIORITY
    priority = df_all.groupby("Machine")[["Risk","OEE"]].mean()
    priority["Priority"] = priority["Risk"]*(100-priority["OEE"])
    priority = priority.sort_values("Priority", ascending=False)

    st.subheader("PM Priority")
    st.dataframe(priority)

    st.subheader("OEE Breakdown")
    st.plotly_chart(px.bar(df_all, x="Machine",
        y=["Availability","Performance","Quality"],
        barmode="group"))

    st.subheader("Trend")
    st.plotly_chart(px.line(df_all, x="Timestamp", y="OEE", color="Machine"))

    st.subheader("Risk Distribution")
    st.plotly_chart(px.histogram(df_all, x="Risk", color="Machine"))

    st.subheader("Heatmap")
    heat = df_all.groupby("Machine")[["Risk","OEE"]].mean()
    st.plotly_chart(px.imshow(heat, text_auto=True))

    df_all.to_csv(POWERBI_PATH, index=False)
    st.success("Export updated")