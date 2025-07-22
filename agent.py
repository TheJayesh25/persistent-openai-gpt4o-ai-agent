from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, Sequence

from operator import add as add_messages
from typing import Annotated

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def get_agent():

    llm = ChatOpenAI(model="gpt-4o")

    def process(state: AgentState):
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("process", process)
    graph.add_edge(START, "process")
    graph.add_edge("process", END)

    return graph.compile()