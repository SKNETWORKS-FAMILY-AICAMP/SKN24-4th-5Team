import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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


@require_POST
def chat_message_create(request):
    payload = json.loads(request.body or '{}')
    conversation_id = payload.get('conversation_id')
    content = (payload.get('content') or '').strip()

    if not content:
        return JsonResponse({'error': '메시지를 입력해주세요.'}, status=400)

    if conversation_id:
        conversation = AdmissionChatConversation.objects.filter(id=conversation_id).first()
    else:
        conversation = None

    if conversation is None:
        conversation = AdmissionChatConversation.objects.create(
            title=content[:40],
            user=request.user if request.user.is_authenticated else None,
            group_label='오늘',
        )

    user_message = AdmissionChatMessage.objects.create(
        conversation=conversation,
        role=AdmissionChatMessage.ROLE_USER,
        content=content,
    )
    assistant_message = AdmissionChatMessage.objects.create(
        conversation=conversation,
        role=AdmissionChatMessage.ROLE_ASSISTANT,
        content="This is a sample response saved from the database-backed chat flow.",
    )
    conversation.save()

    return JsonResponse(
        {
            'conversation': {
                'id': str(conversation.id),
                'title': conversation.title,
                'group': conversation.group_label,
            },
            'messages': [
                {
                    'id': str(user_message.id),
                    'role': user_message.role,
                    'content': user_message.content,
                    'timestamp': user_message.created_at.isoformat(),
                },
                {
                    'id': str(assistant_message.id),
                    'role': assistant_message.role,
                    'content': assistant_message.content,
                    'timestamp': assistant_message.created_at.isoformat(),
                },
            ],
        },
        status=201,
    )


@require_POST
def interview_session_create(request):
    payload = json.loads(request.body or '{}')
    mode = payload.get('mode')

    if mode not in dict(VisaInterviewModeDescription.MODE_CHOICES):
        return JsonResponse({'error': '올바른 인터뷰 모드를 선택해주세요.'}, status=400)

    session = VisaInterviewSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        mode=mode,
        uploaded_file_name=payload.get('uploaded_file_name', ''),
        question_count=payload.get('question_count') or None,
        status=VisaInterviewSession.STATUS_IN_PROGRESS,
    )

    first_question = (
        VisaInterviewQuestion.objects
        .filter(mode=mode, is_active=True)
        .order_by('order', 'id')
        .first()
    )

    return JsonResponse(
        {
            'session': {
                'id': session.id,
                'mode': session.mode,
                'status': session.status,
            },
            'question': {
                'id': first_question.id,
                'text': first_question.question_text,
            } if first_question else None,
        },
        status=201,
    )
