from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o")

if user_input:
    response = llm.invoke([HumanMessage(content=user_input)])

    st.session_state.messages.append({
        "role": "assistant",
        "content": response.content
    })