# services/visa/api/practice.py

from fastapi import APIRouter, UploadFile, File, Form
from ..runner import run_practice

router = APIRouter()

@router.post("/practice")
async def practice(
    file: UploadFile = File(None),   # PDF (선택)
    answer: str = Form(None),        # 사용자 답변
    topic: str = Form(None)          # 주제 (선택)
):
    req = {
        "file": file,
        "answer": answer,
        "topic": topic,
        "mode": "practice"
    }

    result = await run_practice(req)
    return result