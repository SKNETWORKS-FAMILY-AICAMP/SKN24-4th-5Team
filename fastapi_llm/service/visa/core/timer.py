"""
core/timer.py
─────────────
인터뷰 타이머.
run_timer() 는 별도 스레드에서 실행되며, 시간이 되면 time_up 플래그를 세웁니다.
"""

import time
import threading

# ── 전역 플래그 ───────────────────────────────────────────────────────────────
time_up: bool = False
_lock = threading.Lock()


def reset_timer() -> None:
    """타이머 플래그 초기화 (인터뷰 시작 전 반드시 호출)."""
    global time_up
    with _lock:
        time_up = False


def is_time_up() -> bool:
    with _lock:
        return time_up


def run_timer(duration: int) -> None:
    """
    카운트다운 타이머.

    Parameters
    ----------
    duration : 제한 시간(초)
    """
    global time_up

    for remaining in range(duration, -1, -1):
        mins = remaining // 60
        secs = remaining % 60
        print(f"\r 남은 시간: {mins:02d}:{secs:02d}", end="", flush=True)
        time.sleep(1)

    print("\n 시간 종료, 이번 질문이 끝나면 답변 후 인터뷰가 종료됩니다.")
    with _lock:
        time_up = True


def start_timer_thread(duration: int) -> threading.Thread:
    """타이머를 데몬 스레드로 실행하고 반환합니다."""
    t = threading.Thread(target=run_timer, args=(duration,), daemon=True)
    t.start()
    return t
