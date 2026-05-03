from fastapi_llm.service.visa.api.schemas import HistoryItem, VisaTurnData, VisaTurnRequest, VisaTurnResponse
from fastapi_llm.service.visa.core.timer import should_finish_interview
from fastapi_llm.service.visa.llm.interview_llm import generate_evaluation, generate_question
from fastapi_llm.service.visa.stt.vosk_stt import speech_to_text_from_base64
from fastapi_llm.service.visa.tts.gtts_tts import text_to_speech_base64
from fastapi_llm.service.visa.utils.audio import analyze_audio_base64


async def handle_interview_turn(payload: VisaTurnRequest) -> VisaTurnResponse:
    history = list(payload.history)
    answer_text = payload.user_answer
    audio_features = None

    if not answer_text and payload.audio_base64:
        answer_text = speech_to_text_from_base64(payload.audio_base64, payload.audio_mime)
        print("[visa] stt_result", repr(answer_text), flush=True)

    if payload.audio_base64:
        audio_features = analyze_audio_base64(payload.audio_base64, answer_text or "", payload.audio_mime)

    if answer_text:
        history = _attach_answer(history, payload.current_question, answer_text, audio_features)

    answered_count = sum(1 for item in history if item.answer.strip())
    is_over = should_finish_interview(payload.mode, answered_count, payload.max_q, payload.is_over)

    if is_over:
        evaluation = generate_evaluation(payload.profile_context, history)
        return VisaTurnResponse(
            data=VisaTurnData(
                mode=payload.mode,
                max_q=payload.max_q,
                answer_text=answer_text,
                history=history,
                is_over=True,
                evaluation=evaluation,
            )
        )

    question = generate_question(payload.profile_context, history)
    history.append(HistoryItem(question=question))
    question_audio = text_to_speech_base64(question)

    return VisaTurnResponse(
        data=VisaTurnData(
            mode=payload.mode,
            max_q=payload.max_q,
            question=question,
            question_audio_base64=question_audio,
            question_audio_mime="audio/mpeg" if question_audio else None,
            answer_text=answer_text,
            history=history,
            is_over=False,
        )
    )


def _attach_answer(
    history: list[HistoryItem],
    current_question: str | None,
    answer_text: str,
    audio_features: dict | None,
) -> list[HistoryItem]:
    if history and not history[-1].answer.strip():
        history[-1].answer = answer_text
        history[-1].audio = audio_features
        return history

    if current_question:
        history.append(HistoryItem(question=current_question, answer=answer_text, audio=audio_features))

    return history
