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

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# ---------- Initialise session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in"):
        if not USER_DATA_FILE.exists() or not user_exists(login_username):
            st.warning("⚠️ Username not found. Please register first.")
        else:
            result = login_user(login_username, login_password)
            if result is True:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                create_session(login_username)
                st.balloons()
                st.success(f"🎉 Welcome back, {login_username}!")
                st.info("Go to dashboard by clicking the button below.")
                if st.button("Go to dashboard"):
                    st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(result)

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")
    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    role = st.selectbox("Select your role", ["user", "admin", "analyst"])

    if st.button("Create account"):
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif user_exists(new_username):
            st.error("Username already exists. Choose another one.")
        else:
            # Validate username and password
            valid_user, msg_user = validate_username(new_username)
            valid_pass, msg_pass = validate_password(new_password, new_username)
            strength_ok, strength_msg = check_password_strength(new_password)

            if not valid_user:
                st.error(msg_user)
            elif not valid_pass:
                st.error(msg_pass)
            elif not strength_ok:
                st.error("Password too weak: " + strength_msg)
            else:
                success = register_user(new_username, new_password, role=role)
                if success:
                    st.balloons()
                    st.success(f"✅ Account created with role '{role}'! You can now log in.")
                    st.info("Go to the Login tab and sign in with your new account.")
                else:
                    st.error("❌ Registration failed. Try again.")
