import base64

from fastapi import APIRouter, Request, Header, HTTPException
import os
    
from fastapi_llm.service.visa.api.schemas import VisaTurnRequest, VisaTurnResponse
from fastapi_llm.service.visa.core.interview import handle_interview_turn

router = APIRouter(prefix="/visa", tags=["visa"])

API_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "66b15280d3145859f2e9e42bb8b41db32c85317ceaefba8144a33412cca50bbb")

# 인터뷰 연습 API
@router.post("/interview", response_model=VisaTurnResponse)
async def visa_interview(request: Request) -> VisaTurnResponse:
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        payload = form.get("payload")
        request_payload = VisaTurnRequest.model_validate_json(str(payload or "{}"))
        audio_file = form.get("audio_file")
        if audio_file is not None:
            audio_bytes = await audio_file.read()
            print(
                "[visa] received audio_file",
                getattr(audio_file, "filename", None),
                getattr(audio_file, "content_type", None),
                len(audio_bytes),
                flush=True,
            )
            request_payload.audio_base64 = base64.b64encode(audio_bytes).decode("ascii")
            request_payload.audio_mime = getattr(audio_file, "content_type", None)
    else:
        body = await request.json()
        request_payload = VisaTurnRequest.model_validate(body)

    return await handle_interview_turn(request_payload)
