from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_llm.service.visa.api.interview import router as visa_interview_router


app = FastAPI(title="Visa Interview LLM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(visa_interview_router)


# Health check endpoint
@app.get("/health")
def health_check() -> dict:
    return {"success": True, "data": {"status": "ok"}}

