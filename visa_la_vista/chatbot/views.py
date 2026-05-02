import json
import os
from dotenv import load_dotenv
import httpx

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import (
    AdmissionChatConversation,
    AdmissionChatMessage,
    VisaInterviewModeDescription,
    VisaInterviewQuestion,
    VisaInterviewSession,
)

load_dotenv()

FASTAPI_URL = "https://1r3qiu3k9lvtup-8000.proxy.runpod.net"
FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "")

def _chat_queryset_for_user(request):
    queryset = AdmissionChatConversation.objects.prefetch_related('messages').filter(
        is_deleted=False
    )
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

        full_answer = ""

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
                    # 토큰 모아서 full_answer 구성
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data != "[DONE]":
                            try:
                                token = json.loads(data).get("token", "")
                                full_answer += token
                            except:
                                pass
                    yield line + "\n\n"

        # 스트림 끝난 후 AdmissionChatMessage 저장 (화면 표시용)
        await AdmissionChatMessage.objects.acreate(
            conversation=conversation,
            role=AdmissionChatMessage.ROLE_USER,
            content=content,
        )
        await AdmissionChatMessage.objects.acreate(
            conversation=conversation,
            role=AdmissionChatMessage.ROLE_ASSISTANT,
            content=full_answer,
        )

    return StreamingHttpResponse(stream(), content_type="text/event-stream")


@require_POST
def chat_conversation_delete(request, conversation_id):
    conversation = AdmissionChatConversation.objects.filter(id=conversation_id).first()
    if not conversation:
        return JsonResponse({'error': '대화방 없음'}, status=404)
    conversation.is_deleted = True
    conversation.deleted_at = timezone.now()
    conversation.save()
    return JsonResponse({'ok': True})


# ----------------------------------- pdf version 1 -----------------------------------
# PDF OCR imports
import sys
import shutil
import pytesseract
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyPDFLoader

def extract_text_flattened_pdf(pdf_path: str) -> str:
    """
    PDF에서 텍스트를 추출합니다.
    1차: PyPDFLoader (텍스트 레이어가 있는 PDF - 빠르고 정확)
    2차: OCR fallback (스캔본처럼 텍스트 레이어가 없는 경우)
    """
    import shutil

    # 1차: PyPDFLoader로 텍스트 추출 시도
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text = "\n".join(d.page_content for d in docs).strip()
        if len(text) > 100:   # 텍스트가 충분히 추출되면 바로 반환
            print("[PDF] 텍스트 레이어 추출 성공")
            return text
        print("[PDF] 텍스트 레이어 부족 → OCR 시도")
    except Exception as e:
        print(f"[PDF] PyPDFLoader 실패 → OCR 시도: {e}")

    # 2차: OCR fallback
    from pdf2image import convert_from_path
    import pytesseract

    # poppler
    poppler_bin = shutil.which("pdftocairo")
    if poppler_bin:
        # This automatically finds where brew installed it
        poppler_path = os.path.dirname(poppler_bin)
    else:
        # Fallback for common locations
        if sys.platform == "darwin": # Mac
            poppler_path = "/opt/homebrew/bin" 
        elif sys.platform == "win32": # Windows
            poppler_path = r"C:\Program Files\poppler\Library\bin"
        else: # Linux/AWS
            poppler_path = "/usr/bin"

    # tesseract
    tesseract_bin = shutil.which("tesseract")
    if tesseract_bin:
        pytesseract.pytesseract.tesseract_cmd = tesseract_bin
    elif sys.platform == "win32":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

    try:
        print(f"[OCR] Poppler 경로: {poppler_path}")
        pages = convert_from_path(pdf_path, 300, poppler_path=poppler_path)
        full_text = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            full_text.append(text)
            print(f"[OCR] Page {i + 1} 처리 완료")
        return "".join(full_text)
    except Exception as e:
        return f"[OCR 오류] {e}"



# NEW FUNCTION
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os

def extract_pdf_view(request):
    if request.method == "POST" and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Save file temporarily to disk so PyPDFLoader can read it
        file_name = default_storage.save(f"tmp/{pdf_file.name}", pdf_file)
        file_path = default_storage.path(file_name)

        try:
            # Call your Python function here
            extracted_text = extract_text_flattened_pdf(file_path)
            
            return JsonResponse({
                "status": "success", 
                "text": extracted_text
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        finally:
            # Always clean up the temp file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




# RUNPOD_URL = "https://ruqmxrcp2wvlx8-8000.proxy.runpod.net"
# API_SECRET_KEY = os.getenv("RUNPOT_API_KEY", "7759e342f8e33b061b680498d30d42b6873a21d1cacd060c0a4258d26eaa94ab")
# FASTAPI_SECRET_KEY

@require_POST
# @csrf_exempt
def interview_session_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST만 허용"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': "JSON 형식 오류"}, status=400)


    def stream_generator():
        print(f"Sending request to RunPod: {RUNPOD_URL}/run-agent")
        with httpx.Client(timeout=120.0) as client:
            with client.stream(
                "POST", f"{RUNPOT_URL}/run-agent",
                headers={
                    "x-api-key": API_SECRET_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "task":data.get("task", ""),
                    "pdf_path": data.get("pdf_path", ""),
                    "interview_history": data.get("interview_history",[])
                }
            ) as response:
                for line in response.iter_lines():
                    if line and line != "data: [Done]":
                        yield line + "\n"
            print(f"Response status: {response.status_code}")

    return StreamingHttpResponse(
        stream_generator(),
        content_type = "text/event-stream"
    )
    """
    ### original return format
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
    return JsonResponse({
        'session': {'id': session.id, 'mode': session.mode, 'status': session.status},
        'question': {
            'id': first_question.id,
            'text': first_question.question_text,
        } if first_question else None,
    }, status=201)



    # response data
    # FastAPI가 장고에 돌려주는 실제 인터뷰 처리 결과
    class VisaTurnData(BaseModel):
        mode: InterviewMode
        question: str | None = None
        question_audio_base64: str | None = None
        answer_text: str | None = None
        history: list[HistoryItem]
        is_over: bool
        evaluation: str | None = None
    """