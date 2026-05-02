from fastapi_llm.service.visa.config.settings import settings


def should_finish_interview(mode: str, answered_count: int, max_q: int | None, is_over: bool) -> bool:
    if mode == "real":
        return is_over
    if max_q is None:
        return False
    return answered_count >= max_q


def interview_duration_seconds() -> int:
    return settings.INTERVIEW_DURATION_SECONDS

