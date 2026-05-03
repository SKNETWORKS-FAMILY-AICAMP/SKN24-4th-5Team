# service/admission/service1_agent.py

from dotenv import load_dotenv
load_dotenv(dotenv_path="C:/Users/Playdata/Downloads/web_visa_interview_helper/fastapi_llm/.env")

from .llm.graph import graph
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage

HISTORY_LIMIT = 40

def run_service_1_agent(question: str, s1_chat_history: list | None = None) -> str:
    history = s1_chat_history or []
    recent = history[-HISTORY_LIMIT:]
    full_messages = recent + [{"role": "user", "content": question}]
    last_valid_message = None

    for step in graph.stream({"messages": full_messages}, stream_mode="values"):
        msg = step["messages"][-1]
        print(f"\n[Step]")
        print(f"type: {msg.type}")
        print(f"content: {(msg.content[:80] + '...') if msg.content else 'None'}")

        if msg.type != "ai":
            continue
        if not msg.content:
            continue
        if getattr(msg, "tool_calls", None):
            continue
        if "SELECT" in msg.content or "FROM" in msg.content:
            continue
        last_valid_message = msg.content

    return last_valid_message or "답변을 생성하지 못했습니다."


def web_search_node(state: MessagesState):
    user_query = next(
        m.content for m in reversed(state["messages"])
        if m.type == "human"
    )
    search_query = f'"{user_query}" 입학 학비 공식 사이트'
    print(f"--- [범용 검색 실행] ---: {search_query}")
    search_result = search.run(search_query)

    grounded_prompt = f"""
다음은 '{user_query}'에 대한 웹 검색 결과입니다.
[검색 결과]
{search_result}
---
규칙:
1. 오직 '{user_query}' 정보만 사용하세요.
2. 검색 결과에 '{user_query}' 정보가 없으면 "해당 대학 정보를 찾지 못했습니다"라고만 답하세요.
3. 다른 대학 정보를 절대 혼용하지 마세요.
"""
    return {
        "messages": [HumanMessage(content=grounded_prompt)]
    }