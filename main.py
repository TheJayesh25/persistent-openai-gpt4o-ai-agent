import streamlit as st
import os
import sqlite3
import uuid
import hashlib
from typing import Optional
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
def hash_token(token: str) -> str:
    """Hash the API token for secure session identification."""
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(name: str, user_hash: str) -> str:
    """Create a new session and return its UUID."""
    session_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO sessions (id, name, user_hash) VALUES (?, ?, ?)", (session_id, name, user_hash))
    conn.commit()
    return session_id

def get_sessions_by_user(user_hash: str):
    """Fetch all sessions associated with a user hash."""
    cursor.execute("SELECT id, name FROM sessions WHERE user_hash = ? ORDER BY created_at DESC", (user_hash,))
    return cursor.fetchall()

def serialize_message(msg: BaseMessage, session_id: str):
    """Convert a message into a row format for storage."""
    base = {
        "session_id": session_id,
        "type": msg.type,
        "content": msg.content,
        "name": None,
        "tool_call_id": None
    }
    if isinstance(msg, FunctionMessage):
        base["name"] = msg.name
    elif isinstance(msg, ToolMessage):
        base["tool_call_id"] = msg.tool_call_id
    return base

def deserialize_message(row: tuple) -> BaseMessage:
    """Convert a DB row back to a LangChain message."""
    msg_type, content, name, tool_call_id = row
    if msg_type == "human":
        return HumanMessage(content=content)
    elif msg_type == "ai":
        return AIMessage(content=content)
    elif msg_type == "system":
        return SystemMessage(content=content)
    elif msg_type == "function":
        return FunctionMessage(content=content, name=name or "function_1")
    elif msg_type == "tool":
        return ToolMessage(content=content, tool_call_id=tool_call_id or "tool_1")
    else:
        raise ValueError(f"Unknown message type: {msg_type}")

def load_history(session_id):
    """Load all messages for a given session."""
    cursor.execute("SELECT type, content, name, tool_call_id FROM chat_messages WHERE session_id = ?", (session_id,))
    rows = cursor.fetchall()
    return [deserialize_message(m) for m in rows] if rows else []

def save_history(session_id, new_messages):
    """Save a batch of new messages to the DB."""
    for msg in new_messages:
        data = serialize_message(msg, session_id)
        cursor.execute("""
            INSERT INTO chat_messages (session_id, type, content, name, tool_call_id)
            VALUES (?, ?, ?, ?, ?)
        """, (data["session_id"], data["type"], data["content"], data["name"], data["tool_call_id"]))
    conn.commit()

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
