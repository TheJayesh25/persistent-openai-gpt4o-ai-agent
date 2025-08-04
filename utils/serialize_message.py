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