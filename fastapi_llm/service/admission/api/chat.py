from fastapi import APIRouter
from ..runner import run_admission

router = APIRouter()

@router.post("/chat")
async def chat(req: dict):
    return run_admission(req["message"])