import asyncio
from fastapi import Request
from fastapi.responses import StreamingResponse
from asgiref.sync import sync_to_async
import json

from service.admission.schemas import AgentRequest
from .service1_agent import run_service_1_agent, HISTORY_LIMIT

from chatbot.models import ChatMessage  # FastAPI 전용 히스토리 테이블


async def _run_llm(question: str, history: list):
    return await asyncio.to_thread(run_service_1_agent, question, history)


def _sse_stream(answer: str):
    async def generator():
        for i in range(0, len(answer), 100):
            chunk = answer[i:i+100]
            yield f"data: {json.dumps({'token': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    return generator()


async def chat_v1_logic(agent_request: AgentRequest, http_request: Request):

    chat_id = agent_request.chat_id
    user_id = agent_request.user_id

    # 1. 히스토리 읽기 (ChatMessage - FastAPI 전용)
    rows = await sync_to_async(list)(
        ChatMessage.objects
        .filter(chat_id=chat_id)
        .order_by("created_at")[:HISTORY_LIMIT]
    )

    history = [{"role": r.role, "content": r.content} for r in rows]

    # 2. LLM 실행
    answer = await _run_llm(agent_request.question, history)

    # 3. ChatMessage 저장 (FastAPI 전용, FK 없음)
    def save():
        ChatMessage.objects.bulk_create([
            ChatMessage(
                user_id=user_id,
                chat_id=chat_id,
                role="user",
                content=agent_request.question,
            ),
            ChatMessage(
                user_id=user_id,
                chat_id=chat_id,
                role="assistant",
                content=answer,
            ),
        ])

    await sync_to_async(save, thread_sensitive=True)()

    # 4. SSE 스트리밍
    return StreamingResponse(_sse_stream(answer), media_type="text/event-stream")