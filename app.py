import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

st.set_page_config(page_title="Diabetes Management App", layout="wide")

# -----------------------
# FILE STORAGE (simple DB)
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
def classify_glucose(v):
    if v < 70: return "Low"
    elif v <= 140: return "Normal"
    elif v <= 200: return "High"
    else: return "Critical"

# -----------------------
# AUTH
# -----------------------
def auth():
    st.title("🔐 Login / Signup")
    choice = st.radio("Select", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if username in data["users"]:
                st.error("User exists")
            else:
                data["users"][username] = {"password": password}
                save_data(data)
                st.success("Account created")

    if choice == "Login":
        if st.button("Login"):
            user = data["users"].get(username)
            if user and user["password"] == password:
                st.session_state.user = username
                st.success("Logged in")
            else:
                st.error("Invalid credentials")

# -----------------------
# DASHBOARD
# -----------------------
def dashboard(user):
    st.title("📊 Dashboard")

    gdf = pd.DataFrame(data["glucose"])
    mdf = pd.DataFrame(data["meals"])

    if not gdf.empty:
        gdf = gdf[gdf["user"] == user]
        st.plotly_chart(px.line(gdf, x="time", y="value", title="Glucose Trend"))

    else:
        st.info("No glucose data yet")

    if not mdf.empty:
        mdf = mdf[mdf["user"] == user]
        st.plotly_chart(px.bar(mdf, x="meal", y="sugar", title="Sugar Intake"))
    else:
        st.info("No meal data yet")

# -----------------------
# MAIN APP
# -----------------------
def app():
    user = st.session_state.user
    st.sidebar.title(f"Welcome {user}")

    page = st.sidebar.radio("Menu", ["Dashboard", "Glucose", "Meals", "Logout"])

    if page == "Dashboard":
        dashboard(user)

    elif page == "Glucose":
        st.header("Glucose Tracking")
        val = st.number_input("Glucose", min_value=0)

        if st.button("Save"):
            data["glucose"].append({
                "user": user,
                "value": val,
                "category": classify_glucose(val),
                "time": str(datetime.now())
            })
            save_data(data)
            st.success("Saved")

    elif page == "Meals":
        st.header("Meal Tracking")
        meal = st.text_input("Meal")
        sugar = st.number_input("Sugar", min_value=0)

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
