# services/admission/api/chat.py

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from pydantic import BaseModel

from ..runner import chat_v1_logic, chat_v2_logic
from dotenv import load_dotenv
import os
# load_dotenv(dotenv_path="/workspace/project/env")
load_dotenv(dotenv_path="C:/Users/Playdata/Downloads/web_visa_interview_helper/fastapi_llm/.env")
router = APIRouter()


class AgentRequest(BaseModel):
    user_id: str
    chat_id: str
    question: str


API_SECRET_KEY =  os.getenv("FASTAPI_SECRET_KEY")

def _check_auth(x_api_key: Optional[str]):
    print("👉 받은 KEY:", repr(x_api_key))
    print("👉 ENV KEY:", repr(API_SECRET_KEY))

    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
# def _check_auth(x_api_key: Optional[str]):
#     if x_api_key != API_SECRET_KEY:
#         raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/chat/v1")
async def chat_v1(request: AgentRequest, x_api_key: Optional[str] = Header(None)):
    _check_auth(x_api_key)
    return await chat_v1_logic(request)


@router.post("/chat/v2")
async def chat_v2(request: AgentRequest, x_api_key: Optional[str] = Header(None)):
    _check_auth(x_api_key)
    return await chat_v2_logic(request)



