# ---------- Import required modules ----------
import streamlit as st
import sys
import path as Path

# Add the folder containing auth.py to Python path
AUTH_PATH = Path(r"C:\CST1510\CW2_CST1510_M01041173")
if str(AUTH_PATH) not in sys.path:
    sys.path.append(str(AUTH_PATH))

from auth import (
    register_user,
    login_user,
    user_exists,
    validate_username,
    validate_password,
    check_password_strength,
    create_session,
    USER_DATA_FILE,
    MAX_ATTEMPTS,
    ACCOUNT_LOCK_TIME
)
import time

# ---------- Streamlit Page ----------
st.set_page_config(page_title="Wave", layout="wide", page_icon="logo.png")
st.title("🔐 Welcome to Wave")
st.caption("Register / Login")

# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Login"

# ---------- Redirect if already logged in ----------
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ---------- Tabs ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        if not USER_DATA_FILE.exists() or not user_exists(login_username):
            st.warning("⚠️ Username not found. Please register first.")
            st.session_state.active_tab = "Register"
            st.experimental_rerun()

        login_result = login_user(login_username, login_password)

        if login_result is True:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}!")
            create_session(login_username)

            # Show balloons immediately
            st.balloons()
            st.success("🎉 Login Successful!")

            # Give a "Go to Dashboard" button
            if st.button("Go to Dashboard"):
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.error(login_result)

# ---------- REGISTER TAB -----
with tab_register:
    st.subheader("Register")
    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    # Role selection
    role_options = ["user", "admin", "analyst"]
    selected_role = st.selectbox("Select your role", role_options, index=0)

    if st.button("Create account"):
        valid_user, msg_user = validate_username(new_username)
        if not valid_user:
            st.error(msg_user)
        elif user_exists(new_username):
            st.error("Username already exists.")
        else:
            valid_pass, msg_pass = validate_password(new_password, new_username)
            if not valid_pass:
                st.error(msg_pass)
            else:
                strength_ok, strength_msg = check_password_strength(new_password)
                progress_value = 0.25
                if "Moderate" in strength_msg:
                    progress_value = 0.66
                elif "Strong" in strength_msg:
                    progress_value = 1.0
                st.progress(progress_value)
                st.info(strength_msg)

                if not strength_ok:
                    st.error("Please choose a stronger password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    if register_user(new_username, new_password, role=selected_role):
                        # Show balloons immediately
                        st.balloons()
                        st.success(f"✅ Account created with role '{selected_role}'! You can now log in.")
                        st.info("Please use the Login tab to sign in.")

                        # Optionally auto-switch to Login tab
                        tab_register, tab_login = st.tabs(["Register", "Login"])
                        tab_login.select()  # This will focus the Login tab
                    else:
                        st.error("❌ Registration failed. Try again.")
