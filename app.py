import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------
# SESSION STATE INIT
# ---------------------------
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

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def classify_glucose(value):
    if value < 70:
        return "Low"
    elif 70 <= value <= 140:
        return "Normal"
    elif 140 < value <= 200:
        return "High"
    else:
        return "Critical"

# ---------------------------
# LOGIN / SIGNUP PAGE
# ---------------------------
def auth_page():
    st.title("🔐 Diabetes App Login")

    option = st.radio("Select Option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        role = st.selectbox("Select Role", ["Patient", "Doctor", "Caregiver"])

        if st.button("Create Account"):
            if username in st.session_state.users:
                st.error("User already exists!")
            else:
                st.session_state.users[username] = {
                    "password": password,
                    "role": role
                }
                st.success("Account created! Please login.")

    else:
        if st.button("Login"):
            user = st.session_state.users.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")

# ---------------------------
# DASHBOARD
# ---------------------------
def dashboard():
    user = st.session_state.current_user
    role = st.session_state.users[user]["role"]

    st.title(f"🏥 Welcome {user} ({role})")

    menu = st.sidebar.selectbox("Menu", [
        "Glucose Tracking",
        "Meal Tracking",
        "Profile"
    ])

    if menu == "Glucose Tracking":
        st.header("📊 Blood Glucose Tracking")

        glucose = st.number_input("Enter Glucose Level (mg/dL)", min_value=0)

        if st.button("Save Reading"):
            category = classify_glucose(glucose)
            st.session_state.glucose_data.append({
                "user": user,
                "value": glucose,
                "category": category,
                "time": datetime.now()
            })

            st.success(f"Saved! Category: {category}")

            if category == "Critical":
                st.warning("⚠️ Visit a doctor immediately!")

        df = pd.DataFrame(st.session_state.glucose_data)
        if not df.empty:
            st.subheader("📈 History")
            st.dataframe(df[df["user"] == user])

    elif menu == "Meal Tracking":
        st.header("🍽️ Meal & Nutrition")

        meal = st.text_input("Meal Name")
        calories = st.number_input("Calories", min_value=0)
        sugar = st.number_input("Sugar (g)", min_value=0)

        if st.button("Save Meal"):
            st.session_state.meals.append({
                "user": user,
                "meal": meal,
                "calories": calories,
                "sugar": sugar,
                "time": datetime.now()
            })
            st.success("Meal saved!")

        df = pd.DataFrame(st.session_state.meals)
        if not df.empty:
            st.subheader("🍴 Meal History")
            st.dataframe(df[df["user"] == user])

    elif menu == "Profile":
        st.header("👤 Profile")

        age = st.number_input("Age", min_value=0)
        height = st.number_input("Height (cm)", min_value=0)
        weight = st.number_input("Weight (kg)", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.button("Save Profile"):
            st.session_state.users[user]["profile"] = {
                "age": age,
                "height": height,
                "weight": weight,
                "gender": gender
            }
            st.success("Profile updated!")

        if "profile" in st.session_state.users[user]:
            st.write(st.session_state.users[user]["profile"])

# ---------------------------
# MAIN APP
# ---------------------------
if not st.session_state.logged_in:
    auth_page()
else:
    dashboard()
