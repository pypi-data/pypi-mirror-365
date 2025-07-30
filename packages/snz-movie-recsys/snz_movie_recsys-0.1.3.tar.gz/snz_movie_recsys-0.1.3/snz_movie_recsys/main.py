import os
import getpass
from intro import show_intro
from langchain.chains.summarize.refine_prompts import prompt_template
from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from openai import max_retries
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
import pandas as pd

"""
환경변수 설정
"""
load_dotenv(override=True)

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("TAVILY_API_KEY")

print(f"# OPENAI_API_KEY : {os.environ.get("OPENAI_API_KEY")[:10]}")
print(f"# TAVILY_API_KEY : {os.environ.get("TAVILY_API_KEY")[:10]}")


"""
변수 정의
"""
LLM_MODEL = "gpt-4o-mini"
DATA_FILE_PATH = "/imdb_top_1000.csv"
"""
상태 정의
"""
class MyState(TypedDict):
    messages: List[dict]                 # 전체 대화 기록
    ended: bool                          # 종료 여부
    summary: List[str]                    # 영화 추천 요약
    recommendations: Optional[List[dict]] # 최종 추천 결과

"""
LLM 및 Embedding
"""
llm = ChatOpenAI(model=LLM_MODEL)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

"""
Chatbot 노드 정의
"""
# 1. 챗봇 tool
@tool
def chatbot_tool(state: MyState) -> MyState:
    """사용자의 전체 대화를 기반으로 멀티턴 영화 대화 및 요약"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    messages = state["messages"]
    # 마지막 유저 발화
    last_user_msg = messages[-1]["content"] if messages else "안녕하세요, 오늘 기분이 어떠신가요?"

    # 챗봇 답변 생성
    convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    prompt = f"""
    당신은 영화 추천을 위한 대화를 진행하는 챗봇입니다.
    지금까지 대화:
    {convo}

    사용자의 마지막 발화: {last_user_msg}

    친근하게 한 문장으로 답변하고,
    영화 추천을 위한 대화를 자연스럽게 이어가세요.
    """
    bot_reply = llm.invoke(prompt).content.strip()
    messages.append({"role":"assistant","content":bot_reply})

    # 유저 메시지가 3개 이상이면 요약 생성
    user_msgs = [m["content"] for m in messages if m["role"]=="user"]
    if len(user_msgs) >= 3:
        summary_prompt = f"""
        다음 대화를 영화 추천에 필요한 핵심 정보(감정, 취향) 위주로 1~2문장 요약하세요:
        {convo}
        """
        summary = llm.invoke(summary_prompt).content.strip()
        state["summary"] = [summary]
        state["ended"] = True

    state["messages"] = messages
    return state

# 2. 감성 분석 tool
@tool
def movie_rec_tool(state: MyState) -> MyState:
    """요약 기반으로 imdb_top_1000.csv에서 영화 5개와 추천 사유 생성"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # CSV 로드
    path = "/imdb_top_1000.csv"
    df = pd.read_csv(path)
    df = df[['Series_Title','Genre','Overview']].dropna().drop_duplicates()

    summary = state["summary"][0] if state["summary"] else "사용자 요약 없음"

    # 영화 후보 5개를 선정
    # df에서 랜덤 샘플로 필터링하지 않고 LLM이 선택하도록 프롬프트 제공
    sample_df = df.sample(30, random_state=42)  # LLM 입력 부담 줄이기
    movies_text = "\n".join([
        f"{row.Series_Title} ({row.Genre}): {row.Overview}"
        for _, row in sample_df.iterrows()
    ])

    prompt = f"""
    사용자의 영화 취향 요약:
    {summary}

    아래는 영화 후보 목록입니다:
    {movies_text}

    위 후보 중 사용자 요약에 가장 적합한 영화 5개를 고르고,
    각 영화에 대해 1~2문장으로 추천 사유를 작성하세요.
    보기 좋게 아래 JSON 형식으로 출력하세요:
    [
        {{"title": "영화제목", "reason": "추천 사유"}},
        ...
    ]
    """
    resp = llm.invoke(prompt).content

    import json
    try:
        recommendations = json.loads(resp)
    except:
        # LLM이 JSON 형식이 아닐 경우 대비
        recommendations = [{"title":"추천 실패","reason":resp}]

    # 보기 좋게 출력
    print("=== 🎬 최종 추천 영화 5선 ===")
    for rec in recommendations:
        print(f"- {rec['title']}: {rec['reason']}")

    state["recommendations"] = recommendations
    return state

tools = [chatbot_tool, movie_rec_tool]
agent = create_react_agent(llm, tools)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)






def main():

    # 앱 초기 UI
    show_intro()
    
    """
    LangGraph 상태 그래프 정의
    """
    builder = StateGraph(MyState)
    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "chatbot")
    
    graph = builder.compile()
    # print(graph)



if __name__ == "__main__":
    # 실행
    main() 