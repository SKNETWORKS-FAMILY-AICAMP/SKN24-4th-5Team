# services/visa/api/mock.py

from fastapi import APIRouter, UploadFile, File, Form
from ..runner import run_mock

router = APIRouter()

@router.post("/mock")
async def mock(
    file: UploadFile = File(...),    # 실전은 PDF 필수
    answer: str = Form(None),
):
    req = {
        "file": file,
        "answer": answer,
        "mode": "mock"
    }

    result = await run_mock(req)
    return result