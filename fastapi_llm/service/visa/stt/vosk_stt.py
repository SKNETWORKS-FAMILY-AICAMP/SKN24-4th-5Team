"""
stt/vosk_stt.py
───────────────
Vosk 기반 Speech-to-Text.
모델은 최초 호출 시 한 번만 로드합니다 (싱글턴 패턴).
"""

import json
import wave

from vosk import Model, KaldiRecognizer
from config.settings import STT_MODEL_PATH

# ── 싱글턴 모델 ───────────────────────────────────────────────────────────────
_model: Model | None = None


def _get_model() -> Model:
    global _model
    if _model is None:
        print(f"[STT] Vosk 모델 로드 중: {STT_MODEL_PATH}")
        _model = Model(STT_MODEL_PATH)
        print("[STT] 모델 로드 완료")
    return _model


# ── 공개 함수 ─────────────────────────────────────────────────────────────────

def speech_to_text(audio_path: str) -> str:
    """
    WAV 파일을 Vosk로 텍스트 변환합니다.

    Parameters
    ----------
    audio_path : WAV 파일 경로 (16 kHz, 모노 권장)

    Returns
    -------
    str : 인식된 텍스트
    """
    model = _get_model()

    with wave.open(audio_path, "rb") as wf:
        rec = KaldiRecognizer(model, wf.getframerate())
        result_text = ""

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                result_text += result.get("text", "") + " "

        final = json.loads(rec.FinalResult())
        result_text += final.get("text", "")

    return result_text.strip()
