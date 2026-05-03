import os
import sys

# ── 경로 설정 ──────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))  # fastapi_llm/
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # web_visa_interview_helper/
django_root = os.path.join(project_root, "visa_la_vista")  # visa_la_vista/

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if django_root not in sys.path:
    sys.path.insert(0, django_root)

# ── Django 초기화 ────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visa_la_vista.settings")  # ← visa_la_vista 폴더 안의 settings

import django
django.setup()

# ── FastAPI ─────────────────────────────────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from service.admission.api import chat
from fastapi_llm.service.visa.api.interview import router as visa_interview_router





app = FastAPI(title="Service Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/admission")
app.include_router(visa_interview_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


#pip install python-multipart