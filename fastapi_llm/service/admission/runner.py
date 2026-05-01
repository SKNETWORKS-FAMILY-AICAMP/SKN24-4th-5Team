from dotenv import load_dotenv
 
load_dotenv(dotenv_path="/workspace/project/env")
 
from graph import graph
 
HISTORY_LIMIT = 40


def run_service_1_agent(question: str, s1_chat_history: list | None = None) -> str:
    """
    s1_chat_history: AWS RDS에서 가져온 최근 대화 리스트
    형태: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    history = s1_chat_history or []
    recent = history[-HISTORY_LIMIT:]

    full_messages = recent + [{"role": "user", "content": question}]
    
    result = ""
    
    for step in graph.stream({"messages": full_messages}, stream_mode = "values"):
        message = step["messages"][-1]
        if message.type == "ai" and message.content and not message.tool_calls:
            result = message.content
    return result