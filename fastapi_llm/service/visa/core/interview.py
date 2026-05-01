"""
core/interview.py
============================
인터뷰 상태 관리 + 메인 루프.

Public API
======함수 설명======
start_interview()          - 인터뷰 시작 (상태 초기화)
stop_interview()           - 인터뷰 강제 종료
interview_loop(mode, ...)  - 메인 루프
run_practice_mode()        - 연습모드 진입점
run_real_mode()            - 실전모드 진입점
"""

import time
import threading

from config.settings import REAL_MODE_TIMER_SEC, AUTO_START_DELAY_SEC, AUDIO_FILENAME
from core.timer import reset_timer, is_time_up, start_timer_thread
from llm.interview_llm import get_question, get_final_evaluation, save_feedback_pdf
from stt.vosk_stt import speech_to_text
from tts.piper_tts import text_to_speech_practice, text_to_speech_real
from utils.audio import record

# ── 상태 변수 ─────────────────────────────────────────────────────────────────
_is_running : bool = False # 인터뷰 진행 중 여부
_is_stopped : bool = False # 강제 종료 여부
_start_time : float | None = None # 인터뷰 시작 시간 (초 단위 타임스탬프)

# 다른 모듈에서 profile_context 를 주입받기 위한 변수
profile_context: str = "" # 사용자 PDF에서 추출한 텍스트


# ═════════════════════════════════════════════════════════════════════════════
# 상태 제어
# ═════════════════════════════════════════════════════════════════════════════

def start_interview() -> None:
    """인터뷰 상태를 초기화하고 시작합니다."""
    global _is_running, _is_stopped, _start_time
    _is_running = True
    _is_stopped = False
    _start_time = time.time()
    reset_timer()


def stop_interview() -> None:
    """인터뷰를 강제 종료합니다."""
    global _is_running, _is_stopped
    _is_running = False
    _is_stopped = True


# ═════════════════════════════════════════════════════════════════════════════
# 메인 루프
# ═════════════════════════════════════════════════════════════════════════════

def interview_loop(mode: str, max_questions: int | None = None) -> None:
    """
    인터뷰 메인 루프.

    Parameters
    ----------
    mode          : "practice" | "real"
    max_questions : 연습모드에서 최대 질문 수 (실전모드에서는 무시)
    """
    global _is_running, _is_stopped

    # 실전모드: 타이머 스레드 시작
    if mode == "real":
        start_timer_thread(REAL_MODE_TIMER_SEC)

    history       : list[dict] = []
    used_refs     : set[str]   = set()
    question_count: int        = 0

    while _is_running:

        # 강제 종료 체크
        if _is_stopped:
            return

        # ── 질문 생성 ──────────────────────────────────────────────────────
        question = get_question(profile_context, history, used_refs)

        if mode == "practice":
            print(f"\nOfficer: {question}")
            text_to_speech_practice(question)

        elif mode == "real":
            print("\nOfficer: (음성으로 질문이 제공됩니다)")
            text_to_speech_real(question)

        # ── 사용자 답변 녹음 & STT ─────────────────────────────────────────
        if mode == "practice":
            record(AUDIO_FILENAME)
            user_answer = speech_to_text(AUDIO_FILENAME)

        elif mode == "real":
            print(f"{AUTO_START_DELAY_SEC}초 후 자동 녹음 시작...")
            time.sleep(AUTO_START_DELAY_SEC)
            record(AUDIO_FILENAME, auto_start=True)
            user_answer = speech_to_text(AUDIO_FILENAME)

        print(f"User: {user_answer}")

        history.append({"question": question, "answer": user_answer})
        question_count += 1

        # ── 종료 조건 ──────────────────────────────────────────────────────
        if mode == "practice" and max_questions and question_count >= max_questions:
            break

        if mode == "real" and is_time_up():
            print("\n 시간 종료(인터뷰 종료)")
            break

    # ── 최종 평가 ──────────────────────────────────────────────────────────
    final_evaluation = get_final_evaluation(profile_context, history)

    print("\n" + "=" * 50)
    print("Final Interview Result")
    print("=" * 50)
    print(final_evaluation)

    # ── PDF 저장 여부 확인 ─────────────────────────────────────────────────
    while True:
        save_input = input("\n 최종 피드백 결과를 PDF로 저장하시겠습니까? (예/아니오): ").strip()

        if save_input == "예":
            save_feedback_pdf(final_evaluation)
            break
        elif save_input == "아니오":
            print("저장을 건너뜁니다.")
            break
        else:
            print("예 또는 아니오로 입력해주세요.")


# ═════════════════════════════════════════════════════════════════════════════
# 모드별 진입점
# ═════════════════════════════════════════════════════════════════════════════

def run_practice_mode() -> None:
    """연습모드: 질문 개수를 입력받고 인터뷰를 시작합니다."""
    max_q = int(input("질문 개수 입력 (1~10): "))
    start_interview()
    interview_loop("practice", max_q)


def run_real_mode() -> None:
    """실전모드: 타이머 기반 인터뷰를 시작합니다."""
    start_interview()
    interview_loop("real")
