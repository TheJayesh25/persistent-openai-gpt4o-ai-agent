import streamlit as st
import os
import sqlite3
import uuid
import hashlib
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    FunctionMessage,
    ToolMessage,
    BaseMessage,
)
from agent import get_agent

# -------------------- DATABASE SETUP --------------------
db_path = os.path.join(os.path.dirname(__file__), "chat_messages.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        user_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        type TEXT CHECK(type IN ('human', 'ai', 'system', 'tool', 'function')) NOT NULL,
        content TEXT NOT NULL,
        name TEXT,
        tool_call_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# -------------------- UTILITIES --------------------
from utils.hash_token import hash_token
from utils.create_session import create_session
from utils.get_sessions_by_user import get_sessions_by_user
from utils.serialize_message import serialize_message
from utils.deserialize_message import deserialize_message
from utils.history_manager import load_history, save_history

# -------------------- AUTH GATE (OPENAI API) --------------------
st.set_page_config(page_title="GPT-4o Agent", page_icon="🧠")

if "openai_api_key" not in st.session_state:
    st.title("🔐 GPT-4o Agent (OpenAI)")
    st.markdown("""
    This app uses **OpenAI GPT-4o** via your own API key.

    🔑 Please enter your **OpenAI API key** to continue.

    - You can create one here: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
    """)

    token_input = st.text_input("Enter your OpenAI API Key:", type="password")

    if st.button("Start Chatting") and token_input:
        try:
            # Validate token by invoking a test query
            temp_agent = get_agent(token_input)
            _ = temp_agent.invoke({"messages": [HumanMessage(content="Hello!")]})
            st.session_state["openai_api_key"] = token_input
            st.session_state["user_hash"] = hash_token(token_input)
            st.rerun()
        except Exception:
            st.error("❌ Invalid token. Please check and try again.")
    st.stop()

# -------------------- STREAMLIT APP --------------------
st.title("🧠 GPT-4o Assistant (OpenAI)")

# ---- SIDEBAR SESSION MANAGER ----
with st.sidebar:
    st.header("💬 Sessions")

    if "user_hash" not in st.session_state:
        st.error("Authentication error. Please log in again.")
        st.stop()

    sessions = get_sessions_by_user(st.session_state["user_hash"])
    session_names = [s[1] for s in sessions]
    selected_option = st.selectbox("Select session", session_names + ["➕ New session"])

    if selected_option == "➕ New session":
        new_session_name = st.text_input("Enter session name")
        if new_session_name and st.button("Create Session"):
            selected_id = create_session(new_session_name, st.session_state["user_hash"])
            st.session_state.session_id = selected_id
            st.session_state.messages = []
            st.rerun()
        elif "session_id" not in st.session_state:
            st.stop()
        else:
            selected_id = st.session_state.session_id
    else:
        selected_id = next(s[0] for s in sessions if s[1] == selected_option)
        if st.session_state.get("session_id") != selected_id:
            st.session_state.session_id = selected_id
            st.session_state.messages = load_history(selected_id)
            st.rerun()

    st.markdown("---")
    if st.button("🔒 Log out"):
        for k in ["openai_api_key", "user_hash", "session_id", "messages"]:
            st.session_state.pop(k, None)
        st.rerun()

# ---- INITIALIZE MEMORY ----
if "messages" not in st.session_state:
    history = load_history(st.session_state.session_id)
    if not history:
        history = [SystemMessage(content="You are a helpful assistant. Answer concisely.")]
    st.session_state.messages = history

# ---- DISPLAY CHAT MESSAGES ----
for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage):
        continue
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# ---- CHAT INPUT ----
user_input = st.chat_input("Ask me anything...")

if user_input:
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")

    agent = get_agent(st.session_state["openai_api_key"])
    result = agent.invoke({"messages": st.session_state.messages})

    new_messages = result["messages"][len(st.session_state.messages):]
    st.session_state.messages = result["messages"]

    if new_messages:
        bot_reply = new_messages[0].content
        placeholder.markdown(bot_reply)

    save_history(st.session_state.session_id, [user_msg, new_messages[0]])
