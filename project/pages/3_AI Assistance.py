import streamlit as st
from openai import OpenAI
import os
import sys

# ------------ DB + Modules ------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

from app.data.db import connect_database, load_all_csv_data, save_message, load_messages
from app.data.schema import create_all_tables

# ------------------- OPENAI -----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------- LOGIN CHECK -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("You must be logged in.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# ------------------- GET USER -------------------
username = st.session_state.get("username")
if not username:
    st.error("Username not found in session.")
    st.stop()

# ------------------- DATABASE -------------------
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DB_FILE = os.path.join(DATA_DIR, "intelligence_platform.db")
conn = connect_database(DB_FILE)
create_all_tables(conn)

# Ensure user exists in DB
def ensure_user(conn, username):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password_hash)
        VALUES (?, ?)
    """, (username, "dummy"))
    conn.commit()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    return cursor.fetchone()[0]  # numeric user_id

user_id = ensure_user(conn, username)

# Optional: Load CSV data into DB
load_all_csv_data(conn, os.path.join(DATA_DIR, "cyber_incidents.csv"), "cyber_incidents")
load_all_csv_data(conn, os.path.join(DATA_DIR, "it_tickets.csv"), "it_tickets")
load_all_csv_data(conn, os.path.join(DATA_DIR, "datasets_metadata.csv"), "datasets_metadata")

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Wave - AI Assistant", layout="wide", page_icon="logo.png")

# ------------------- DOMAIN SELECTOR -------------------
domain = st.sidebar.selectbox("Select Domain", ["Cybersecurity", "IT Operations", "Data Science"])

# ------------------- SYSTEM PROMPTS -------------------
domain_prompts = {
    "Cybersecurity": """
You are a cybersecurity expert AI assistant.
- Analyze incidents and threats
- Provide technical guidance
- Explain attack vectors and mitigations
- Use standard terminology (MITRE ATT&CK, CVE)
- Prioritize actionable recommendations
Tone: Professional, technical
Format: Clear, structured responses
""",
    "IT Operations": """
You are an IT operations specialist AI assistant.
- Troubleshoot systems, networking, cloud, databases
- Provide step-by-step ITIL-based solutions
""",
    "Data Science": """
You are a Data Science expert.
- Explain ML models, preprocessing, pandas, sklearn 
- Provide Python examples when needed
"""
}

# ------------------- INITIALIZE SESSION STATE -------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

user_key = f"{username}_{domain}"

if user_key not in st.session_state.chat_history:
    messages = load_messages(conn, user_id, domain)

    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": domain_prompts[domain]})
    st.session_state.chat_history[user_key] = messages

messages = st.session_state.chat_history[user_key]


# ------------------- DOMAIN HEADER -------------------
st.markdown(
    f"""
    <div style='font-weight: bold; font-size:28px; text-align:center; 
    color:#0b3d91; border-bottom:3px solid #ff4b4b; margin-top:20px;'>{domain} Chatbot
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Powered by GPT-4o")

# ------------------- DISPLAY CHAT -------------------
for message in messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.subheader("Chat Controls")
    message_count = len([m for m in messages if m["role"] != "system"])
    st.metric("Messages", message_count)

    if st.button("🗑 Clear Chat", use_container_width=True):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id=? AND domain=?", (user_id, domain))
        conn.commit()
        st.session_state.chat_history[user_key] = [{"role": "system", "content": domain_prompts[domain]}]
        st.toast("Chat cleared!", icon="🧹")
        st.rerun()

    # ---- DOWNLOAD CHAT (PURE FILE HANDLING VERSION) ----
    chat_filename = f"{username}_{domain}_chat.txt"

    # Create the file using pure file handling
    with open(chat_filename, "w", encoding="utf-8") as file:
        for m in messages:
            if m["role"] != "system":
                file.write(f"{m['role'].upper()}:\n{m['content']}\n\n")

    # Download button
    with open(chat_filename, "rb") as file:
        st.sidebar.download_button(
            label="📥 Download Chat",
            data=file,
            file_name=chat_filename,
            mime="text/plain",
            use_container_width=True
        )   

    model = st.selectbox("Model", ["gpt-4o"], index=0)
    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1,
        help="Higher values make output more random"
    )


# ------------------- USER INPUT -------------------
prompt = st.chat_input(f"Ask about {domain.lower()}...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.chat_history[user_key].append({"role": "user", "content": prompt})
    save_message(conn, user_id, domain, "user", prompt)

    # OpenAI Streaming response
    with st.spinner("Thinking..."):
        completion = client.chat.completions.create(
            model=model,
            messages=st.session_state.chat_history[user_key],
            temperature=temperature,
            stream=True
        )

        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""
            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_reply += delta.content
                    container.markdown(full_reply + "▌")
            container.markdown(full_reply)

        st.session_state.chat_history[user_key].append({"role": "assistant", "content": full_reply})
        save_message(conn, user_id, domain, "assistant", full_reply)
