import streamlit as st
import os
import hashlib
from agent import get_agent
import uuid
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    FunctionMessage,
    ToolMessage,
    BaseMessage,
)
import sqlite3

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

st.title("GPT Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

agent = get_agent()
response = agent([HumanMessage(content=user_input)])