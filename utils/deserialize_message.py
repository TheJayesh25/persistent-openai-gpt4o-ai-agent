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