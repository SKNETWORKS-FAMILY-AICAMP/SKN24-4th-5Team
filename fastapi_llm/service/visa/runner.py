from fastapi_llm.service.visa.api.schemas import VisaTurnRequest, VisaTurnResponse
from fastapi_llm.service.visa.core.interview import handle_interview_turn


async def run_visa_interview_turn(payload: VisaTurnRequest) -> VisaTurnResponse:
    return await handle_interview_turn(payload)

