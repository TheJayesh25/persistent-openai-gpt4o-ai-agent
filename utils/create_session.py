import uuid
def create_session(name: str, user_hash: str) -> str:
    """Create a new session and return its UUID."""
    session_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO sessions (id, name, user_hash) VALUES (?, ?, ?)", (session_id, name, user_hash))
    conn.commit()
    return session_id