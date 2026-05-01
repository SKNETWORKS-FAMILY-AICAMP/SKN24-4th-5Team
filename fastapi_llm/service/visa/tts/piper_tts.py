"""
tts/piper_tts.py
────────────────
Piper TTS 래퍼. Windows / macOS 모두 동작합니다.

- text_to_speech_practice : 연습모드용 (고정 파일명, 덮어쓰기)
- text_to_speech_real     : 실전모드용 (타임스탬프 파일명, 재생 후 삭제)

재생 방식:
  Windows → winsound (내장, 설치 불필요)
  macOS   → afplay   (내장, 설치 불필요)
"""

import os
import sys
import subprocess
import time

from config.settings import TTS_EXE_PATH, TTS_MODEL_PATH


# ── WAV 재생 ─────────────────────────────────────────────────────────────────

def _play_wav(filepath: str) -> None:
    """OS에 맞는 방식으로 WAV 파일을 동기 재생합니다."""
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(filepath, winsound.SND_FILENAME)
    else:
        # macOS: afplay (내장)
        subprocess.run(["afplay", filepath], check=True)


# ── Piper 실행 ────────────────────────────────────────────────────────────────

def _run_piper(text: str, output_file: str) -> None:
    """
    Piper TTS를 실행해 WAV 파일을 생성합니다.
    Windows / macOS 모두 subprocess.run + stdin 방식으로 통일합니다.
    (echo 명령어가 OS마다 동작이 달라 stdin 방식이 더 안정적)
    """
    cmd = [TTS_EXE_PATH, "--model", TTS_MODEL_PATH, "--output_file", output_file]
    subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        check=True,
    )


# ── 공개 함수 ─────────────────────────────────────────────────────────────────

def text_to_speech_practice(text: str) -> None:
    """연습모드 TTS. 타임스탬프 파일명으로 저장 → 재생 → 삭제."""
    output_file = f"output_{int(time.time() * 1000)}.wav"
    _run_piper(text, output_file)
    _play_wav(output_file)
    if os.path.exists(output_file):
        os.remove(output_file)


def text_to_speech_real(text: str) -> None:
    """실전모드 TTS. 타임스탬프 파일명으로 저장 → 재생 → 삭제."""
    output_file = f"output_{int(time.time() * 1000)}.wav"
    _run_piper(text, output_file)
    _play_wav(output_file)

    if os.path.exists(output_file):
        os.remove(output_file)
