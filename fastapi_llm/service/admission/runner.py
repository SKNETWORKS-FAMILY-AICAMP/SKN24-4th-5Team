import asyncio
from fastapi import Request
from fastapi.responses import StreamingResponse
from asgiref.sync import sync_to_async
import json

from service.admission.schemas import AgentRequest
from .service1_agent import run_service_1_agent, HISTORY_LIMIT

from chatbot.models import AdmissionChatConversation, AdmissionChatMessage


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

    # 1. 대화 히스토리 읽기
    rows = await sync_to_async(list)(
        AdmissionChatMessage.objects
        .filter(conversation_id=chat_id)
        .order_by("created_at")[:HISTORY_LIMIT]
    )

    history = [{"role": r.role, "content": r.content} for r in rows]

    # 2. LLM 실행
    answer = await _run_llm(agent_request.question, history)

    # 3. DB 저장
    def save():
        AdmissionChatMessage.objects.bulk_create([
            AdmissionChatMessage(
                conversation_id=chat_id,
                role="user",
                content=agent_request.question,
            ),
            AdmissionChatMessage(
                conversation_id=chat_id,
                role="assistant",
                content=answer,
            ),
        ])

    await sync_to_async(save, thread_sensitive=True)()

    # 4. SSE 스트리밍
    return StreamingResponse(_sse_stream(answer), media_type="text/event-stream")