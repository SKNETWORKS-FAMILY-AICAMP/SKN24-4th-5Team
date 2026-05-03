from typing import Literal

from pydantic import BaseModel, Field


InterviewMode = Literal["practice", "real"]


# One question-answer pair stored by Django and sent back each turn.
class HistoryItem(BaseModel):
    question: str
    answer: str = ""
    audio: dict | None = None


# Request payload sent from Django to FastAPI for one interview turn.
class VisaTurnRequest(BaseModel):
    mode: InterviewMode
    max_q: int | None = Field(default=None, ge=1)
    profile_context: str = ""
    history: list[HistoryItem] = Field(default_factory=list)
    is_over: bool = False
    user_answer: str | None = None
    current_question: str | None = None
    audio_base64: str | None = None
    audio_mime: str | None = "audio/mpeg"


# Actual interview turn result returned from FastAPI to Django.
class VisaTurnData(BaseModel):
    mode: InterviewMode
    max_q: int | None = None
    question: str | None = None
    question_audio_base64: str | None = None
    question_audio_mime: str | None = None
    answer_text: str | None = None
    history: list[HistoryItem]
    is_over: bool
    evaluation: str | None = None


# Common response wrapper for visa interview API responses.
class VisaTurnResponse(BaseModel):
    success: bool = True
    data: VisaTurnData
