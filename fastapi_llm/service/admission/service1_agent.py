# services/admission/llm/service1_agent.py

from dotenv import load_dotenv
# load_dotenv(dotenv_path="/workspace/project/env")
load_dotenv(dotenv_path="C:/Users/Playdata/Downloads/web_visa_interview_helper/fastapi_llm/.env")

from .llm.graph import graph   

HISTORY_LIMIT = 40


# def run_service_1_agent(question: str, s1_chat_history: list | None = None) -> str:

#     history = s1_chat_history or []
#     recent = history[-HISTORY_LIMIT:]

#     full_messages = recent + [{"role": "user", "content": question}]
    
#     result = ""
    
#     # for step in graph.stream({"messages": full_messages}, stream_mode="values"):
#     #     message = step["messages"][-1]
#     #     if message.type == "ai" and message.content and not message.tool_calls:
#     #         result = message.content

#     for step in graph.stream({"messages": full_messages}, stream_mode="values"):
#         # 현재 단계의 마지막 메시지 추출
#         message = step["messages"][-1]
        
#         # --- 디버깅 로그 시작 ---
#         print(f"\n[Step Trace]")
#         print(f"Type: {message.type}")
#         # 내용이 너무 길면 앞부분 100자만 출력
#         content_snippet = (message.content[:100] + '...') if message.content else "None"
#         print(f"Content: {content_snippet}")
        
#         # 도구 호출(SQL 생성 등)이 있는지 확인
#         if hasattr(message, 'tool_calls') and message.tool_calls:
#             print(f"도구 호출 발견: {message.tool_calls}")
#         # --- 디버깅 로그 끝 ---

#         if message.type == "ai" and message.content and not message.tool_calls:
#             result = message.content




#     return result

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