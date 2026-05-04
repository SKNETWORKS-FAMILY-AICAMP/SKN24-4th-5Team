import json
import os
from dotenv import load_dotenv
import httpx

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from .models import (
    AdmissionChatConversation,
    AdmissionChatMessage,
    VisaInterviewModeDescription,
    VisaInterviewQuestion,
    VisaInterviewSession,
)

load_dotenv()

# S1 Runpod FASTAPI
FASTAPI_URL = os.getenv("FASTAPI_URL")
FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")

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

    user = await request.auser()

    if conversation_id:
        conversation = await AdmissionChatConversation.objects.filter(id=conversation_id).afirst()
    else:
        conversation = None

    if conversation is None:
        conversation = await AdmissionChatConversation.objects.acreate(
            title=content[:40],
            user=user if user.is_authenticated else None,  
            group_label='오늘',
        )

    user_id = str(user.id) if user.is_authenticated else "anonymous"  
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



# S2 Runpod FASTAPI
import httpx
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

FASTAPI_URL = os.getenv("FASTAPI_URL")
FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")

import base64

@csrf_exempt
@require_POST
def interview_session_create(request):
    try:
        if request.content_type and "multipart" in request.content_type:
            payload_raw = request.POST.get("payload", "{}")
            audio_file = request.FILES.get("audio_file")
        else:
            payload_raw = request.body.decode("utf-8") if request.body else "{}"
            audio_file = None

        try:
            data = json.loads(payload_raw)
        except json.JSONDecodeError:
            return JsonResponse({'error': "payload JSON 형식 오류"}, status=400)

        max_q = data.get("max_q", 2)
        if max_q in (None, ""):
            max_q = None
        else:
            max_q = int(max_q)

        payload = {
            "mode": data.get("mode", "practice"),
            "max_q": max_q,
            "profile_context": data.get("profile_context", ""),
            "history": data.get("history", []),
            "is_over": bool(data.get("is_over", False)),
            "user_answer": data.get("user_answer") or None,
            "current_question": data.get("current_question") or None,
        }

        audio_bytes = None
        audio_content_type = None
        if audio_file:
            audio_bytes = audio_file.read()
            audio_content_type = audio_file.content_type or "audio/wav"

            print(f"[audio received] name={audio_file.name}, size={len(audio_bytes)} bytes, type={audio_content_type}")
        else:
            print("[audio received] NO audio file — sending JSON only")

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None

        if audio_base64:
            payload["audio_base64"] = audio_base64
            payload["audio_mime"] = audio_content_type
            print(f"[audio base64] length={len(audio_base64)} chars")

        if not FASTAPI_URL:
            return JsonResponse({'error': "FASTAPI_URL 환경변수가 설정되지 않았습니다."}, status=500)

        target_url = f"{FASTAPI_URL.rstrip('/')}/visa/interview"
    except Exception as e:
        print(f"[interview request error] {e}")
        return JsonResponse({'error': f"인터뷰 요청 처리 중 오류가 발생했습니다: {str(e)}"}, status=500)

    def stream_generator():
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            try:
                with client.stream(
                    "POST", target_url,
                    headers={"x-api-key": FASTAPI_SECRET_KEY},
                    json=payload,   # audio_base64 + audio_mime are inside here
                ) as response:
                    print(f"[runpod] response status: {response.status_code}")

                    if response.status_code != 200:
                        error_body = response.read()
                        error_text = error_body.decode(errors="replace")
                        print(f"[runpod] error body: {error_text}")
                        error_payload = json.dumps({
                            "success": False,
                            "error": f"AI 서버 오류가 발생했습니다. ({response.status_code})",
                            "detail": error_text,
                        }, ensure_ascii=False)
                        yield error_payload
                        return

                    for line in response.iter_lines():
                        if line:
                            yield line + "\n"

            except httpx.ConnectTimeout:
                yield "data: Connection timed out.\n\n"
            except Exception as e:
                print(f"[stream error] {e}")
                yield f"data: Server error: {str(e)}\n\n"

    return StreamingHttpResponse(stream_generator(), content_type="text/event-stream")



async def before_multipart_audio_interview_session_create(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': "JSON 형식 오류"}, status=400)

    payload = {
        "mode": data.get("mode", "practice"),
        "max_q": int(data.get("max_q", 2)),
        "profile_context": data.get("profile_context", ""),
        "history": data.get("history", []),
        "is_over": False,
        "user_answer": data.get("user_answer") or None,
        "current_question": data.get("current_question") or None,
    }

    target_url = f"{FASTAPI_URL.rstrip('/')}/visa/interview"  # No trailing slash

    async def stream_generator():
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            try:
                async with client.stream(
                    "POST",
                    target_url,
                    headers={"x-api-key": FASTAPI_SECRET_KEY},
                    # This replicates requests' data= param (form field, not file)
                    # data={"payload": json.dumps(payload, ensure_ascii=False)},
                     json=payload,  
                ) as response:
                    print(f"FastAPI response status: {response.status_code}")

                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield f"data: Error {response.status_code}: {error_body.decode()}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n"

            except httpx.ConnectTimeout:
                yield "data: Connection timed out.\n\n"
            except Exception as e:
                print(f"Stream error: {e}")
                yield f"data: Server error: {str(e)}\n\n"

    return StreamingHttpResponse(
        stream_generator(),
        content_type="text/event-stream"
    )


@csrf_exempt
@require_POST
def original_interview_session_create(request):
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
                    "x-api-key": FASTAPI_SECRET_KEY,
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
                        print(f"Proxying line: {line}")
                        yield line + "\n"
            print(f"Response status: {response.status_code}")

    return StreamingHttpResponse(
        stream_generator(),
        content_type = "text/event-stream"
    )
