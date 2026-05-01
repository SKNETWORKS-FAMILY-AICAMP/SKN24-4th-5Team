import json
import os
import httpx

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST

from .models import (
    AdmissionChatConversation,
    AdmissionChatMessage,
    VisaInterviewModeDescription,
    VisaInterviewQuestion,
    VisaInterviewSession,
)

FASTAPI_URL = "http://127.0.0.1:8001"
FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "")


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
                'id': str(c.id),
                'title': c.title,
                'group': c.group_label,
                'messages': [
                    {
                        'id': str(m.id),
                        'role': m.role,
                        'content': m.content,
                        'timestamp': m.created_at.isoformat(),
                    }
                    for m in c.messages.all()
                ],
            }
            for c in conversations
        ],
        'activeConversationId': str(active_conversation.id) if active_conversation else None,
        'messages': [
            {
                'id': str(m.id),
                'role': m.role,
                'content': m.content,
                'timestamp': m.created_at.isoformat(),
            }
            for m in (active_conversation.messages.all() if active_conversation else [])
        ],
    }


def _serialize_interview_page_data():
    mode_descriptions = {
        item.mode: {'title': item.title, 'text': item.description}
        for item in VisaInterviewModeDescription.objects.all()
    }
    questions = {'practice': [], 'real': []}
    for q in VisaInterviewQuestion.objects.filter(is_active=True):
        questions.setdefault(q.mode, []).append(
            {'id': q.id, 'text': q.question_text, 'order': q.order}
        )
    return {
        'modeDescriptions': mode_descriptions,
        'questions': questions,
        'questionCounts': list(range(1, 11)),
    }


def chat_list(request):
    return render(request, 'chatbot/chat_page.html', {'chat_page_data': _serialize_chat_page_data(request)})


def interview_page(request):
    return render(request, 'chatbot/interview_page.html', {'interview_page_data': _serialize_interview_page_data()})


def get_history(request, chat_id):
    messages = AdmissionChatMessage.objects.filter(
        conversation_id=chat_id
    ).order_by("created_at")
    return JsonResponse({
        'messages': [
            {
                'id': str(m.id),
                'role': m.role,
                'content': m.content,
                'timestamp': m.created_at.isoformat(),
            }
            for m in messages
        ]
    })


@require_POST
async def chat_message_create(request):
    payload = json.loads(request.body or '{}')
    conversation_id = payload.get('conversation_id')
    content = (payload.get('content') or '').strip()

    if not content:
        return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)

    if conversation_id:
        conversation = await AdmissionChatConversation.objects.filter(id=conversation_id).afirst()
    else:
        conversation = None

    if conversation is None:
        conversation = await AdmissionChatConversation.objects.acreate(
            title=content[:40],
            user=request.user if request.user.is_authenticated else None,
            group_label='오늘',
        )

    user_id = str(request.user.id) if request.user.is_authenticated else "anonymous"
    chat_id = str(conversation.id)
    conv_title = conversation.title
    conv_group = conversation.group_label
    conv_id_str = str(conversation.id)

    async def stream():
        meta = json.dumps({
            "type": "meta",
            "conversation_id": conv_id_str,
            "title": conv_title,
            "group": conv_group,
        }, ensure_ascii=False)
        yield f"data: {meta}\n\n"

        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{FASTAPI_URL}/admission/chat/v1",
                json={"user_id": user_id, "chat_id": chat_id, "question": content},
                headers={"x-api-key": FASTAPI_SECRET_KEY},
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    yield line + "\n\n"

    return StreamingHttpResponse(stream(), content_type="text/event-stream")


def _chat_queryset_for_user(request):
    queryset = AdmissionChatConversation.objects.prefetch_related('messages').filter(
        is_deleted=False  # ← 추가
    )
    if request.user.is_authenticated:
        user_queryset = queryset.filter(user=request.user)
        if user_queryset.exists():
            return user_queryset
    return queryset.filter(user__isnull=True)

from django.utils import timezone

@require_POST
def chat_conversation_delete(request, conversation_id):
    conversation = AdmissionChatConversation.objects.filter(id=conversation_id).first()
    if not conversation:
        return JsonResponse({'error': '대화방 없음'}, status=404)
    conversation.is_deleted = True
    conversation.deleted_at = timezone.now()
    conversation.save()
    return JsonResponse({'ok': True})

# @require_POST
# def interview_session_create(request):
#     payload = json.loads(request.body or '{}')
#     mode = payload.get('mode')
#     if mode not in dict(VisaInterviewModeDescription.MODE_CHOICES):
#         return JsonResponse({'error': '올바른 인터뷰 모드를 선택해주세요.'}, status=400)
#     session = VisaInterviewSession.objects.create(
#         user=request.user if request.user.is_authenticated else None,
#         mode=mode,
#         uploaded_file_name=payload.get('uploaded_file_name', ''),
#         question_count=payload.get('question_count') or None,
#         status=VisaInterviewSession.STATUS_IN_PROGRESS,
#     )
#     first_question = (
#         VisaInterviewQuestion.objects
#         .filter(mode=mode, is_active=True)
#         .order_by('order', 'id')
#         .first()
#     )
#     return JsonResponse({
#         'session': {'id': session.id, 'mode': session.mode, 'status': session.status},
#         'question': {
#             'id': first_question.id,
#             'text': first_question.question_text,
#         } if first_question else None,
#     }, status=201)