import asyncio
import json
from functools import partial
from asgiref.sync import sync_to_async  
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from django.db import transaction

from .service1_agent import run_service_1_agent, HISTORY_LIMIT

import sys
import os

# api -> admission -> service -> fastapi_llm 
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_path not in sys.path:
    sys.path.append(root_path)

from chatbot.models import ChatMessage, ChatSession

async def _run_graph(question, history):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, partial(run_service_1_agent, question, history)
    )


def _sse_stream(answer: str):
    async def generator():
        for i in range(0, len(answer), 100):
            chunk = answer[i:i+100]
            yield f"data: {json.dumps({'token': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    return generator()


def _streaming_response(answer):
    return StreamingResponse(
        _sse_stream(answer),
        media_type="text/event-stream",
    )


async def chat_v1_logic(request):

    rows = await sync_to_async(list)(
        ChatMessage.objects
        .filter(user_id=request.user_id, chat_id=request.chat_id)
        .order_by("-created_at")[:HISTORY_LIMIT]
    )

    history = [
        {"role": r.role, "content": r.content}
        for r in reversed(rows)
    ]

    answer = await _run_graph(request.question, history)

   # 3. DB 저장 로직을 별도 함수로 분리 (안정성 확보)
    def save_messages():
        with transaction.atomic():
            ChatMessage.objects.bulk_create([
                ChatMessage(user_id=request.user_id, chat_id=request.chat_id, role="user", content=request.question),
                ChatMessage(user_id=request.user_id, chat_id=request.chat_id, role="assistant", content=answer)
            ])

    # 4. sync_to_async로 감싸서 실행 (뒤에 () 붙이지 마세요!)
    await sync_to_async(save_messages, thread_sensitive=True)()

    return _streaming_response(answer)

async def chat_v2_logic(request):
    # 1. 세션 가져오기 혹은 생성 (JSON 데이터가 들어있는 모델)
    session, _ = await sync_to_async(
        lambda: ChatSession.objects.get_or_create(
            user_id=request.user_id,
            chat_id=request.chat_id,
            defaults={"messages": []}
        )
    )()

    # 2. 기존 JSON 리스트에서 히스토리 추출
    history = session.messages[-HISTORY_LIMIT:]

    # 3. 그래프 실행 (답변 생성)
    answer = await _run_graph(request.question, history)

    # 4. JSON 필드 업데이트 로직을 별도 함수로 분리
    def save_session_json():
        with transaction.atomic():
            # 기존 리스트에 새 대화 추가 (Python 리스트 연산)
            new_messages = session.messages + [
                {"role": "user", "content": request.question},
                {"role": "assistant", "content": answer},
            ]
            # DB에 반영
            session.messages = new_messages
            session.save(update_fields=["messages", "updated_at"])

    # 5. 비동기 환경에서 동기 저장 함수 실행
    await sync_to_async(save_session_json, thread_sensitive=True)()

    # 6. 결과 반환
    return _streaming_response(answer)