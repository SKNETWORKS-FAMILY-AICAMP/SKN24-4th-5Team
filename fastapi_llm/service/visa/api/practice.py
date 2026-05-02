# services/visa/api/practice.py

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from service.visa.runner import run_practice

load_dotenv(dotenv_path="C:/Users/Playdata/Downloads/web_visa_interview_helper/fastapi_llm/.env")

router = APIRouter()
API_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")


def _check_auth(x_api_key: Optional[str]) -> None:
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/practice")
async def practice(
    file: UploadFile = File(None),
    answer: str = Form(None),
    topic: str = Form(None),
    x_api_key: Optional[str] = Header(None),   # 인증 추가
):
    _check_auth(x_api_key)

    req = {
        "file": file,
        "answer": answer,
        "topic": topic,
        "mode": "practice",
    }

    result = await run_practice(req)
    return result