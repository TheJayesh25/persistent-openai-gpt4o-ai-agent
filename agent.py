from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence
from operator import add as add_messages

class AgentState(TypedDict):
    """
    Defines the state of the LangGraph agent.
    Uses `Annotated` to automatically accumulate messages using `add_messages`.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

def make_process(llm):
    def process(state: AgentState) -> AgentState:
        """
        Node function that takes in a state (with all previous messages),
        invokes the LLM, and returns the new message to be appended.
        """
        response = llm.invoke(state["messages"])
        return {"messages": [response]}  # LangGraph will merge this with previous state
    return process

def get_agent(api_key: str):
    """
    Constructs and compiles a LangGraph agent with memory-based state handling.
    Returns the compiled agent ready to invoke.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=api_key  # Use session key here
    )

    graph = StateGraph(AgentState)
    graph.add_node("process", make_process(llm))
    graph.add_edge(START, "process")
    graph.add_edge("process", END)
    return graph.compile()
