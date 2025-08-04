def get_sessions_by_user(user_hash: str):
    """Fetch all sessions associated with a user hash."""
    cursor.execute("SELECT id, name FROM sessions WHERE user_hash = ? ORDER BY created_at DESC", (user_hash,))
    return cursor.fetchall()