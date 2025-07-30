# --------------------------------------------------
# requirements
# pip install langgraph==0.0.*  langchain-core openai tiktoken
# pip install sentence-transformers pandas scikit-learn
# --------------------------------------------------

import os, json, pandas as pd
from typing import List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langgraph.graph import StateGraph, END, START


class MyState(TypedDict):
    messages: List[dict]               
    ended: bool                       
    summary: List[str]                 
    recommendations: Optional[List[dict]] 


llm = ChatOpenAI(model="gpt-4o-mini")  
embed = OpenAIEmbeddings()


imdb_df = pd.read_csv("imdb_top_1000.csv")     
imdb_df["plot_emb"] = imdb_df["plot"].map(embed.embed_query)

MAX_TURNS = 3       

def chatbot(state: MyState) -> MyState:

    messages = [HumanMessage(**m) if m["role"]=="user"
                else AIMessage(**m) for m in state["messages"]]

    assistant_resp = llm.invoke(messages)
    messages.append(assistant_resp)

    user_turns = sum(1 for m in messages if m.type == "human")
    ended = user_turns >= MAX_TURNS

    return {
        "messages": [m.dict() for m in messages],
        "ended": ended,
        "summary": state.get("summary", []),
        "recommendations": state.get("recommendations"),
    }

def summarize(state: MyState) -> MyState:

    if state["summary"]:         
        return state

    summary_prompt = [
        {"role":"system",
         "content":"아래 대화를 영화 취향을 파악하기 위한 1-2문장으로 요약해줘."},
        {"role":"user",
         "content": json.dumps(state["messages"], ensure_ascii=False)}
    ]
    summary_resp = llm.invoke(summary_prompt).content.strip()

    new_state = state.copy()
    new_state["summary"] = [summary_resp]
    return new_state

def recommend(state: MyState) -> MyState:

    if state["recommendations"]:
        return state

    query = " ".join(state["summary"])
    query_emb = embed.embed_query(query)

    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity([query_emb], list(imdb_df["plot_emb"]))[0]
    top_idx = sims.argsort()[-5:][::-1]

    recs = [
        {
            "title": imdb_df.iloc[i]["title"],
            "similarity": float(sims[i]),
            "why": f"대화 요약과의 유사도 {sims[i]:.3f}"
        }
        for i in top_idx
    ]

    new_state = state.copy()
    new_state["recommendations"] = recs
    return new_state


builder = StateGraph(MyState)

builder.add_node("chatbot", chatbot)
builder.add_node("summarize", summarize)
builder.add_node("recommend", recommend)

builder.add_edge(START, "chatbot")

# multistep loop: ended 가 False 면 chatbot 으로, True 면 summarize 로
def need_more_chat(state: MyState) -> str:
    return "chatbot" if not state["ended"] else "summarize"

builder.add_conditional_edges(
    "chatbot",
    need_more_chat,
    conditional_edge_mapping={
        "chatbot": "chatbot",
        "summarize": "summarize",
    },
)

builder.add_edge("summarize", "recommend")
builder.add_edge("recommend", END)

graph = builder.compile()

if __name__ == "__main__":
    state: MyState = {
        "messages": [],
        "ended": False,
        "summary": [],
        "recommendations": None,
    }

    # loop
    while not state["ended"]:
        user_input = input("You: ")
        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state)    
        print("AI:", state["messages"][-1]["content"])

    final_state = graph.invoke(state)

    print("\n=== 요약 ===")
    print(final_state["summary"][0])

    print("\n=== 추천 영화 Top 5 ===")
    for r in final_state["recommendations"]:
        print(f"- {r['title']} ({r['similarity']:.3f})")