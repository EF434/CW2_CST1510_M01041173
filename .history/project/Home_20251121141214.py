import streamlit as st
from auth import (
    register_user,
    login_user,
    user_exists,
    validate_username,
    validate_password,
    check_password_strength,
    create_session,
    USER_DATA_FILE
)

# ---------- Page Setup ----------
st.set_page_config(page_title="Wave", layout="centered", page_icon="logo.png")
st.title("🔐 Welcome to Wave")
st.caption("Register / Login")

# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False

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

    if st.button("Log in", key="login_btn"):
        if not USER_DATA_FILE.exists() or not user_exists(login_username):
            st.warning("⚠️ Username not found. Please register first.")
        else:
            login_result = login_user(login_username, login_password)
            if login_result is True:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                create_session(login_username)
                st.balloons()
                st.success(f"🎉 Welcome, {login_username}!")

                if st.button("Go to Dashboard"):
                    st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(login_result)

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    role_options = ["user", "admin", "analyst"]
    selected_role = st.selectbox("Select your role", role_options)

    if st.button("Create account", key="register_btn"):
        # Validate username
        valid_user, msg_user = validate_username(new_username)
        if not valid_user:
            st.error(msg_user)
        elif user_exists(new_username):
            st.error("Username already exists.")
        else:
            # Validate password
            valid_pass, msg_pass = validate_password(new_password, new_username)
            if not valid_pass:
                st.error(msg_pass)
            else:
                # Check password strength
                strength_ok, strength_msg = check_password_strength(new_password)
                st.info(strength_msg)

                if not strength_ok:
                    st.error("Please choose a stronger password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    # Register user
                    success = register_user(new_username, new_password, role=selected_role)
                    st.session_state.registration_success = success

# ----- Show success message and balloons -----
if st.session_state.registration_success:
    st.balloons()
    st.success(f"✅ Account created successfully! You can now log in.")
    st.session_state.registration_success = False
