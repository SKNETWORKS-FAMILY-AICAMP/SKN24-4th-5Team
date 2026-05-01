from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional
from service.admission.schemas import AgentRequest
from ..runner import chat_v1_logic
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="C:/Users/Playdata/Downloads/web_visa_interview_helper/fastapi_llm/.env")
router = APIRouter()

API_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")

def _check_auth(x_api_key: Optional[str]):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/chat/v1")
async def chat_v1(agent_request: AgentRequest, http_request: Request, x_api_key: Optional[str] = Header(None)):
    _check_auth(x_api_key)
    return await chat_v1_logic(agent_request, http_request)