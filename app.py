import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from hashlib import sha256

st.set_page_config(page_title="Diabetes Management App", layout="wide")

if "users" not in st.session_state:
    st.session_state.users = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "glucose_data" not in st.session_state:
    st.session_state.glucose_data = []
if "meals" not in st.session_state:
    st.session_state.meals = []

def hash_pw(pw):
    return sha256(pw.encode()).hexdigest()

def classify_glucose(value):
    if value < 70:
        return "Low"
    elif value <= 140:
        return "Normal"
    elif value <= 200:
        return "High"
    else:
        return "Critical"

def auth():
    st.title("🔐 Login / Signup")
    choice = st.radio("Select", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        role = st.selectbox("Role", ["Patient", "Doctor", "Caregiver"])
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.error("User exists")
            else:
                st.session_state.users[username] = {
                    "password": hash_pw(password),
                    "role": role
                }
                st.success("Account created")

    if choice == "Login":
        if st.button("Login"):
            user = st.session_state.users.get(username)
            if user and user["password"] == hash_pw(password):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Logged in")
            else:
                st.error("Invalid credentials")

def dashboard(user):
    st.title("📊 Dashboard")

    gdf = pd.DataFrame(st.session_state.glucose_data)
    mdf = pd.DataFrame(st.session_state.meals)

    if not gdf.empty:
        gdf = gdf[gdf["user"] == user]
        fig = px.line(gdf, x="time", y="value", title="Glucose Trend")
        st.plotly_chart(fig)

    if not mdf.empty:
        mdf = mdf[mdf["user"] == user]
        fig = px.bar(mdf, x="meal", y="sugar", title="Sugar Intake")
        st.plotly_chart(fig)

def app():
    user = st.session_state.current_user
    st.sidebar.title("Menu")
    choice = st.sidebar.radio("Go to", ["Dashboard", "Glucose", "Meals", "Profile", "Logout"])

    if choice == "Dashboard":
        dashboard(user)

    elif choice == "Glucose":
        st.header("Glucose Tracking")
        val = st.number_input("Glucose", min_value=0)
        if st.button("Save"):
            cat = classify_glucose(val)
            st.session_state.glucose_data.append({
                "user": user,
                "value": val,
                "category": cat,
                "time": datetime.now()
            })
            st.success(f"Saved ({cat})")

    elif choice == "Meals":
        st.header("Meal Tracking")
        meal = st.text_input("Meal")
        sugar = st.number_input("Sugar", min_value=0)
        if st.button("Save Meal"):
            st.session_state.meals.append({
                "user": user,
                "meal": meal,
                "sugar": sugar,
                "time": datetime.now()
            })
            st.success("Saved")

    elif choice == "Profile":
        st.header("Profile")
        st.write("User:", user)

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.current_user = None

if not st.session_state.logged_in:
    auth()
else:
    app()
