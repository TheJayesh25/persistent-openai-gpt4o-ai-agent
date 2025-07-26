import streamlit as st
import os
from agent import get_agent
import uuid
from langchain_core.messages import (
    HumanMessage,
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

def save_message(role, content):
    cursor.execute(
        "INSERT INTO chat_messages (role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()

def load_messages():
    cursor.execute("SELECT role, content FROM chat_messages")
    return cursor.fetchall()

st.set_page_config(page_title="GPT Assistant")

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