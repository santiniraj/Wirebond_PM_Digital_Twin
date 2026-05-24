# =========================================
# 🏭 WIRE BOND SCADA DIGITAL TWIN
# COLOR SAFE + PRESCRIPTIVE AI + PM DATE + FULL FEATURES
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, timedelta
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
.digital {font-size:22px;font-weight:bold;color:#2b6cb0;}
.soft-green {color:#2f855a;}
.soft-orange {color:#b7791f;}
.soft-blue {color:#3182ce;}
.soft-gray {color:#4a5568;}
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
# HIL LOG (Operator Decisions)
# =========================================
HIL_FILE = "hil_log.csv"

try:
    hil_log = pd.read_csv(HIL_FILE)
except:
    hil_log = pd.DataFrame(columns=["Time","Machine","Risk","System_Action","Operator_Decision"])

def log_hil(machine, risk, system_action, operator):
    new = pd.DataFrame([{
        "Time": datetime.now(),
        "Machine": machine,
        "Risk": risk,
        "System_Action": system_action,
        "Operator_Decision": operator
    }])
    global hil_log
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
# SAFE COLOR ENGINE (NO RED MACHINE COLORS)
# =========================================
def soft_risk_color(v):
    if v < 0.3:
        return "#2f855a"  # soft green
    elif v < 0.7:
        return "#d69e2e"  # soft amber
    return "#718096"      # soft gray (NOT red)

# =========================================
# PRESCRIPTIVE + AGENTIC AI ENGINE (RULE BASED)
# =========================================
def ai_diagnosis(wear, temp, speed):
    if wear > 200:
        issue = "Mechanical degradation in bonding head"
        action = "Schedule immediate maintenance inspection"
    elif temp > 320:
        issue = "Thermal instability detected"
        action = "Reduce heater temperature and inspect thermal control"
    elif speed < 1200:
        issue = "Production inefficiency detected"
        action = "Adjust bonding speed calibration"
    else:
        issue = "System operating normally"
        action = "Continue operation"

    return issue, action

# =========================================
# PM DATE CALCULATOR (REAL DATE, NOT TEXT ONLY)
# =========================================
def pm_schedule(wear):
    today = datetime.today()

    if wear < 100:
        return "Routine Maintenance", today + timedelta(days=14)
    elif wear < 200:
        return "Preventive Maintenance", today + timedelta(days=7)
    else:
        return "Urgent Maintenance Required", today + timedelta(days=1)

# =========================================
# 📊 PERFORMANCE DASHBOARD (HISTORICAL)
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
    col4.metric("Overall Efficiency", f"{oee:.2f}%")

    # RISK GAUGE (SOFT COLOR)
    st.subheader("Risk Level Indicator")

    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk*100,
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":soft_risk_color(risk)},
            "steps":[
                {"range":[0,30],"color":"#e6fffa"},
                {"range":[30,70],"color":"#fefcbf"},
                {"range":[70,100],"color":"#edf2f7"}
            ]
        }
    )))

    # AI + PRESCRIPTIVE OUTPUT
    issue, action = ai_diagnosis(wear,temp,speed)

    pm_type, pm_date = pm_schedule(wear)

    st.subheader("System Analysis Report")
    st.info(f"Issue Detected: {issue}")
    st.warning(f"Recommended Action: {action}")

    st.success(f"Maintenance Type: {pm_type}")
    st.write(f"Recommended Maintenance Date: {pm_date.strftime('%Y-%m-%d')}")

    st.subheader("Operator Decision History")
    st.dataframe(hil_log[hil_log["Machine"] == machine_id])

# =========================================
# 🧪 SIMULATION ENGINE
# =========================================
if page == "🧪 Simulation Engine":

    st.title("🧪 Simulation & Intelligent Decision Engine")

    temp = st.sidebar.slider("Bond Temperature",290,330,310)
    speed = st.sidebar.slider("Bond Speed",1000,3000,1500)
    force = st.sidebar.slider("Bond Force",10,100,50)
    wear = st.sidebar.slider("Capillary Wear",0,300,100)

    sim = pd.DataFrame([{
        "Bond_Head_Temperature": temp,
        "Bonding_Speed": speed,
        "Bonding_Force": force,
        "Capillary_Wear": wear
    }])

    X = sim.reindex(columns=features, fill_value=0)
    prob = model.predict_proba(X)[0][1]

    risk = prob

    issue, action = ai_diagnosis(wear,temp,speed)
    pm_type, pm_date = pm_schedule(wear)

    st.subheader("Risk Gauge (Simulation)")
    st.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk*100,
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":soft_risk_color(risk)}
        }
    )))

    st.info(f"Detected Issue: {issue}")
    st.warning(f"Recommended Action: {action}")

    st.success(f"Maintenance Plan: {pm_type}")
    st.write(f"Scheduled Date: {pm_date.strftime('%Y-%m-%d')}")

    st.subheader("Human Approval Layer")

    system_decision = "Approve Maintenance" if risk > 0.5 else "Continue Operation"

    operator = st.radio("Operator Decision",["Approve","Reject"])

    if st.button("Confirm Decision"):
        log_hil(machine_id, risk, system_decision, operator)
        st.success("Decision Recorded")

# =========================================
# 📡 ANALYTICS FEED (POWER BI STYLE)
# =========================================
if page == "📡 Analytics Feed":

    st.title("📡 Industrial Analytics Feed")

    df_all["Availability"] = 1 - df_all["Capillary_Wear"]/300
    df_all["Performance"] = df_all["Bonding_Speed"]/3000
    df_all["Quality"] = 1 - df_all["Wirebond_Failure"]

    df_all["Efficiency"] = df_all["Availability"]*df_all["Performance"]*df_all["Quality"]*100
    df_all["Risk"] = df_all["Capillary_Wear"]/300

    df_all["Timestamp"] = pd.date_range(
        end=pd.Timestamp.now(),
        periods=len(df_all),
        freq="h"
    )

    # PRIORITY ENGINE
    priority = df_all.groupby("Machine")[["Risk","Efficiency"]].mean()
    priority["Priority Score"] = priority["Risk"]*(100-priority["Efficiency"])
    priority = priority.sort_values("Priority Score", ascending=False)

    st.subheader("Maintenance Priority Ranking")
    st.dataframe(priority)

    # VISUALS (SOFT COLORS)
    st.subheader("Efficiency Trend")
    st.plotly_chart(px.line(df_all, x="Timestamp", y="Efficiency", color="Machine"))

    st.subheader("Risk Distribution")
    st.plotly_chart(px.histogram(df_all, x="Risk", color="Machine"))

    st.subheader("System Health Overview")
    heat = df_all.groupby("Machine")[["Risk","Efficiency"]].mean()
    st.plotly_chart(px.imshow(heat, text_auto=True, color_continuous_scale="Blues"))

    st.subheader("Component Analysis")
    st.plotly_chart(px.bar(df_all, x="Machine",
        y=["Availability","Performance","Quality"],
        barmode="group"))

    df_all.to_csv(POWERBI_PATH, index=False)
    st.success("Analytics Export Updated")