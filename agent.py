from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

def get_agent():
    llm = ChatOpenAI(model="gpt-4o")

    def run(messages):
        return llm.invoke(messages)

    return run