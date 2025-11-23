import streamlit as st
import pandas as pd


# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Intelligence Platform",
                   page_icon="🛡️", layout="wide")

# --- SESSION STATE MANAGEMENT ---
# This keeps the user logged in as they interact with the app
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("CYBER INTEL 🛡️")

# --- LOGIN / REGISTER PAGE ---
if not st.session_state.logged_in:
    st.header("🔐 Secure Login System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # Tab 1: Login
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")

            if submit_login:
                # Using your Week 8/Week 7 Logic here
                success, msg = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(msg)
                    st.rerun()  # Reloads the page to show the dashboard
                else:
                    st.error(msg)

    # Tab 2: Register
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            submit_reg = st.form_submit_button("Register")

            if submit_reg:
                if new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    # Using your Service Logic
                    success, msg = register_user(new_user, new_pass)
                    if success:
                        st.success(msg + " Please go to Login tab.")
                    else:
                        st.error(msg)

# --- MAIN DASHBOARD (Only visible if logged in) ---
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("📊 Cyber Incidents Dashboard")

    # Navigation within the dashboard
    choice = st.sidebar.radio("Menu", ["View Incidents", "Report Incident"])

    # --- VIEW INCIDENTS (READ & DELETE) ---
    if choice == "View Incidents":
        st.subheader("Live Incident Feed")

        # Load data using your Week 8 function
        try:
            df = get_all_incidents()  # This returns a pandas DataFrame

            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Incidents", len(df))
            col2.metric("Open Cases", len(df[df['status'] == 'Open']))
            col3.metric("High Severity", len(df[df['severity'] == 'High']))

            # Show the Data
            st.dataframe(df, use_container_width=True)

            # Delete Section
            st.divider()
            st.warning("⚠️ Administrative Zone")
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                id_to_delete = st.number_input(
                    "Enter Incident ID to Delete", min_value=0, step=1)
            with del_col2:
                if st.button("Delete Incident"):
                    # Connect to DB to delete
                    conn = connect_database()
                    delete_incident(conn, id_to_delete)
                    conn.close()
                    st.success(f"Incident #{id_to_delete} deleted.")
                    st.rerun()

        except Exception as e:
            st.error(f"Error connecting to database: {e}")

    # --- REPORT INCIDENT (CREATE) ---
    elif choice == "Report Incident":
        st.subheader("📝 Report New Security Incident")

        with st.form("incident_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                i_type = st.selectbox(
                    "Type", ["Phishing", "Malware", "DDoS", "Data Leak", "Ransomware"])
                severity = st.select_slider(
                    "Severity", ["Low", "Medium", "High", "Critical"])

            with col2:
                status = st.selectbox(
                    "Status", ["Open", "Investigating", "Resolved", "Closed"])
                desc = st.text_area("Description")

            submitted = st.form_submit_button("Submit Report")

            if submitted:
                # Using your Week 8 Insert function
                conn = connect_database()
                # Note: Ensuring date format matches what Week 8 expects (String YYYY-MM-DD)
                incident_id = insert_incident(
                    str(date),
                    i_type,
                    severity,
                    status,
                    desc,
                    st.session_state.username
                )
                st.success(f"Incident Reported! Reference ID: #{incident_id}")