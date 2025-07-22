import streamlit as st
from agent import get_agent

agent = get_agent()
response = agent([HumanMessage(content=user_input)])

import sqlite3

conn = sqlite3.connect("chat_messages.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT
)
""")

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