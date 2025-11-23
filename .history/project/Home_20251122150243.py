# Import requried modules
import streamlit as st
from auth import (
    register_user,
    login_user,
    user_exists,
    validate_username,
    validate_password,
    check_password_strength,
    create_session,
    USER_DATA_FILE,
)

# ---------- Streamlit Page Config ----------
st.set_page_config(page_title="Wave", layout="wide", page_icon="logo.png")
st.image("path_to_banner_image.png", use_column_width=True)
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
    if st.button("🔗 Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    # ---- Login Button ----
    if st.button("Log In", type="primary"):
        # 1. Check empty fields before calling login_user()
        if not login_username:
            st.error("❌ Username must not be empty.")

        elif not login_password:
            st.error("❌ Password must not be empty.")

        # 2. Check if user exists
        elif not USER_DATA_FILE.exists() or not user_exists(login_username):
            st.error(f"❌ Username '{login_username}' not found. Please register first.")

        # 3. Valid input 
        else:
            login_result = login_user(login_username, login_password)

            if login_result is True:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"🎉 Welcome back, {login_username}!")
                create_session(login_username)
                st.balloons()
            else:
                st.error(login_result)

    # ---- Show dashboard button if logged in ----
    if st.session_state.logged_in:
        if st.button("🔗 Dashboard"):
            st.switch_page("pages/1_Dashboard.py")


# ----- REGISTER TAB -----
with tab_register:
        st.subheader("Register")
        
        # Ask for username & password
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

                    # Map strength to progress bar
                    strength_map = {"Weak": 0.25, "Moderate": 0.66, "Strong": 1.0}
                    st.progress(strength_map.get(strength_msg.split()[0], 0.25))
                    st.info(strength_msg)

                    if not strength_ok:
                        st.error("Please choose a stronger password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        if register_user(new_username, new_password, role=selected_role):
                            st.balloons()
                            st.success(f"✅ Account created with role '{selected_role}'! You can now log in.")
                            # Automatically switch to Login tab next render
                            st.session_state.active_tab = "Login"
                            st.session_state.account_created = True
                        else:
                            st.error("❌ Registration failed. Try again.")
