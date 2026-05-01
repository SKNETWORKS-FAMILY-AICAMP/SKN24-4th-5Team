from fastapi import FastAPI
from services.admission.api import chat
from services.visa.api import practice, mock

app = FastAPI()

# 입시 챗봇
app.include_router(chat.router, prefix="/admission")

# 인터뷰 연습
app.include_router(practice.router, prefix="/visa")

# 인터뷰 실전
app.include_router(mock.router, prefix="/visa")