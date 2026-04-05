import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

st.set_page_config(page_title="Diabetes App", layout="wide")

# -----------------------
# STYLE (UI IMPROVEMENT)
# -----------------------
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    .card {
        padding: 20px;
        border-radius: 15px;
        background-color: #1c1f26;
        margin-bottom: 20px;
    }
    .title {
        font-size: 28px;
        font-weight: bold;
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# DATA FILE
# -----------------------
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "glucose": [], "meals": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -----------------------
# SESSION
# -----------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------
# HELPERS
# -----------------------
def classify(v):
    if v < 70: return "Low"
    elif v <= 140: return "Normal"
    elif v <= 200: return "High"
    else: return "Critical"

# -----------------------
# AUTH PAGE
# -----------------------
def auth():
    st.markdown("<div class='title'>Diabetes Manager</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = data["users"].get(u)
            if user and user["password"] == p:
                st.session_state.user = u
            else:
                st.error("Invalid")

    with col2:
        st.subheader("Signup")
        u2 = st.text_input("New Username")
        p2 = st.text_input("New Password", type="password")

        if st.button("Create"):
            if u2 in data["users"]:
                st.error("Exists")
            else:
                data["users"][u2] = {"password": p2}
                save_data(data)
                st.success("Created")

# -----------------------
# DASHBOARD
# -----------------------
def dashboard(user):
    st.markdown("<div class='title'>Dashboard</div>", unsafe_allow_html=True)

    gdf = pd.DataFrame(data["glucose"])
    mdf = pd.DataFrame(data["meals"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Glucose Trend")

        if not gdf.empty:
            gdf = gdf[gdf["user"] == user]
            st.plotly_chart(px.line(gdf, x="time", y="value"))
        else:
            st.info("No data")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Sugar Intake")

        if not mdf.empty:
            mdf = mdf[mdf["user"] == user]
            st.plotly_chart(px.bar(mdf, x="meal", y="sugar"))
        else:
            st.info("No data")

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# APP
# -----------------------
def app():
    user = st.session_state.user

    st.sidebar.title(f"👤 {user}")
    page = st.sidebar.radio("", ["Dashboard", "Add Glucose", "Add Meal", "Logout"])

    if page == "Dashboard":
        dashboard(user)

    elif page == "Add Glucose":
        st.subheader("Add Glucose")

        val = st.number_input("Glucose")

        if st.button("Save"):
            data["glucose"].append({
                "user": user,
                "value": val,
                "category": classify(val),
                "time": str(datetime.now())
            })
            save_data(data)
            st.success("Saved")

    elif page == "Add Meal":
        st.subheader("Add Meal")

        meal = st.text_input("Meal")
        sugar = st.number_input("Sugar")

        if st.button("Save Meal"):
            data["meals"].append({
                "user": user,
                "meal": meal,
                "sugar": sugar,
                "time": str(datetime.now())
            })
            save_data(data)
            st.success("Saved")

    elif page == "Logout":
        st.session_state.user = None

# -----------------------
# RUN
# -----------------------
if st.session_state.user is None:
    auth()
else:
    app()
