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

# ---------- Streamlit Config ----------
st.set_page_config(page_title="Secure Authentication", layout="centered", page_icon="🔑")
st.title("🔐 Welcome to Wave")
st.caption("Register or Login")

# ---------- Session State ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_login_tab" not in st.session_state:
    st.session_state.show_login_tab = True  # True = Login first, False = Register first

# ---------- Redirect if already logged in ----------
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ---------- Tab Order ----------
if st.session_state.show_login_tab:
    tabs = ["Login", "Register"]
else:
    tabs = ["Register", "Login"]

tab1, tab2 = st.tabs(tabs)

if st.session_state.show_login_tab:
    tab_login, tab_register = tab1, tab2
else:
    tab_register, tab_login = tab1, tab2

# ---------- LOGIN TAB ----------
with tab_login:
    st.subheader("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In"):
        if not login_username or not login_password:
            st.error("Username and password are required.")
        elif not USER_DATA_FILE.exists() or not user_exists(login_username):
            st.error(f"Username '{login_username}' not found. Please register first.")
        else:
            result = login_user(login_username, login_password)
            if result is True:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"🎉 Welcome back, {login_username}!")
                create_session(login_username)
                st.balloons()
            else:
                st.error(result)

    if st.session_state.logged_in:
        if st.button("Go to Dashboard"):
            st.switch_page("pages/1_Dashboard.py")

# ---------- REGISTER TAB ----------
with tab_register:
    st.subheader("Register")
    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    role = st.selectbox("Select your role", ["user", "admin", "analyst"], index=0)

    if st.button("Create Account"):
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
                    if register_user(new_username, new_password, role):
                        st.success(f"✅ Account created with role '{role}'! You can now log in.")
                        st.balloons()
                        # Switch to Login tab after registration
                        st.session_state.show_login_tab = True
                        st.experimental_rerun()
                    else:
                        st.error("❌ Registration failed. Try again.")
