from serialize_message import serialize_message
from deserialize_message import deserialize_message

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