import json
import httpx

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST


FASTAPI_URL = "http://127.0.0.1:8001"
FASTAPI_SECRET_KEY = "66b15280d3145859f2e9e42bb8b41db32c85317ceaefba8144a33412cca50bbb"

from .models import (
    AdmissionChatConversation,
    AdmissionChatMessage,
    VisaInterviewModeDescription,
    VisaInterviewQuestion,
    VisaInterviewSession,
)


def _chat_queryset_for_user(request):
    queryset = AdmissionChatConversation.objects.prefetch_related('messages')

    if request.user.is_authenticated:
        user_queryset = queryset.filter(user=request.user)
        if user_queryset.exists():
            return user_queryset

    return queryset.filter(user__isnull=True)


def _serialize_chat_page_data(request):
    conversations = list(_chat_queryset_for_user(request)[:20])
    active_conversation = conversations[0] if conversations else None

    return {
        'conversations': [
            {
                'id': str(conversation.id),
                'title': conversation.title,
                'group': conversation.group_label,
                'messages': [
                    {
                        'id': str(message.id),
                        'role': message.role,
                        'content': message.content,
                        'timestamp': message.created_at.isoformat(),
                    }
                    for message in conversation.messages.all()
                ],
            }
            for conversation in conversations
        ],
        'activeConversationId': str(active_conversation.id) if active_conversation else None,
        'messages': [
            {
                'id': str(message.id),
                'role': message.role,
                'content': message.content,
                'timestamp': message.created_at.isoformat(),
            }
            for message in (active_conversation.messages.all() if active_conversation else [])
        ],
    }


def _serialize_interview_page_data():
    mode_descriptions = {
        item.mode: {
            'title': item.title,
            'text': item.description,
        }
        for item in VisaInterviewModeDescription.objects.all()
    }

    questions = {
        'practice': [],
        'real': [],
    }
    for question in VisaInterviewQuestion.objects.filter(is_active=True):
        questions.setdefault(question.mode, []).append(
            {
                'id': question.id,
                'text': question.question_text,
                'order': question.order,
            }
        )

    return {
        'modeDescriptions': mode_descriptions,
        'questions': questions,
        'questionCounts': list(range(1, 11)),
    }

# @login_required(login_url='uauth:login')  # TODO: 챗봇 화면 구현 중 임시로 로그인 제한 해제
def chat_list(request):
    return render(
        request,
        'chatbot/chat_page.html',
        {'chat_page_data': _serialize_chat_page_data(request)},
    )

# @login_required(login_url='uauth:login')  # TODO: 챗봇 화면 구현 중 임시로 로그인 제한 해제
def interview_page(request):
    return render(
        request,
        'chatbot/interview_page.html',
        {'interview_page_data': _serialize_interview_page_data()},
    )


# @require_POST
# def chat_message_create(request):
#     payload = json.loads(request.body or '{}')
#     conversation_id = payload.get('conversation_id')
#     content = (payload.get('content') or '').strip()

#     if not content:
#         return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)

#     if conversation_id:
#         conversation = AdmissionChatConversation.objects.filter(id=conversation_id).first()
#     else:
#         conversation = None

#     if conversation is None:
#         conversation = AdmissionChatConversation.objects.create(
#             title=content[:40],
#             user=request.user if request.user.is_authenticated else None,
#             group_label='오늘',
#         )

#     user_message = AdmissionChatMessage.objects.create(
#         conversation=conversation,
#         role=AdmissionChatMessage.ROLE_USER,
#         content=content,
#     )
#     assistant_message = AdmissionChatMessage.objects.create(
#         conversation=conversation,
#         role=AdmissionChatMessage.ROLE_ASSISTANT,
#         content="This is a sample response saved from the database-backed chat flow.",
#     )
#     conversation.save()

#     return JsonResponse(
#         {
#             'conversation': {
#                 'id': str(conversation.id),
#                 'title': conversation.title,
#                 'group': conversation.group_label,
#             },
#             'messages': [
#                 {
#                     'id': str(user_message.id),
#                     'role': user_message.role,
#                     'content': user_message.content,
#                     'timestamp': user_message.created_at.isoformat(),
#                 },
#                 {
#                     'id': str(assistant_message.id),
#                     'role': assistant_message.role,
#                     'content': assistant_message.content,
#                     'timestamp': assistant_message.created_at.isoformat(),
#                 },
#             ],
#         },
#         status=201,
#     )
import json
import httpx
import os

from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_POST

FASTAPI_URL = "http://127.0.0.1:8001"
FASTAPI_SECRET_KEY  = os.getenv("FASTAPI_SECRET_KEY")

# @login_required(login_url='/login/')
@require_POST
async def chat_message_stream(request):
    payload = json.loads(request.body or '{}')
    content = (payload.get('content') or '').strip()
    conversation_id = payload.get("conversation_id") or "default"

    if not content:
        return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)

    async def event_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{FASTAPI_URL}/admission/chat/v1",
                json={
                    "user_id": str(request.user.id) if request.user.is_authenticated else "anonymous",
                    "chat_id": conversation_id,
                    "question": content,
                },
                headers={"x-api-key": FASTAPI_SECRET_KEY},
            ) as resp:
                async for chunk in resp.aiter_text():
                    yield chunk

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")


from .models import AdmissionChatConversation

def extract_title(text: str) -> str:
    # 간단 키워드 추출 (앞 15자)
    return text.strip()[:15]


@require_POST
def create_conversation(request):
    payload = json.loads(request.body or '{}')
    content = payload.get('content')
    conversation_id = payload.get('conversation_id')

    # 이미 있으면 패스
    if conversation_id:
        return JsonResponse({"conversation_id": conversation_id})

    # 없으면 새로 생성
    title = extract_title(content)

    conversation = AdmissionChatConversation.objects.create(
        title=title,
        user=request.user if request.user.is_authenticated else None,
        group_label="오늘"
    )

    return JsonResponse({
        "conversation_id": str(conversation.id),
        "title": conversation.title
    })