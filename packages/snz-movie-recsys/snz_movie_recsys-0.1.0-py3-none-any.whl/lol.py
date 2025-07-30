# emotion_chat_graph.py
import os
from typing import Annotated, List, Literal
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]  


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def chat_agent(state: ConversationState) -> dict:
    messages = state["messages"]
    if not messages:
        messages.append(HumanMessage(content="안녕하세요! 오늘 기분이 어떠신가요?"))

    ai_msg = llm.invoke(messages)        
    return {"messages": [ai_msg]}        


builder = StateGraph(ConversationState)
builder.add_node("chat_agent", chat_agent)

builder.add_edge(START, "chat_agent")       
builder.add_edge("chat_agent", "emotion_agent")  
builder.add_edge("emotion_agent", END)      

graph = builder.compile()


if __name__ == "__main__":
    user_input = input("User > ")
    init_state: ConversationState = {
        "messages": [HumanMessage(content=user_input)],
        "emotion": None,
    }

    result = graph.invoke(init_state)
    print("\n ChatGPT :", result["messages"][-1].content)