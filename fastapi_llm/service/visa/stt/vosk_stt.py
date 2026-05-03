import base64
import json
import tempfile
import wave
from pathlib import Path

from fastapi_llm.service.visa.config.settings import settings


def speech_to_text_from_base64(audio_base64: str, audio_mime: str | None = None) -> str:
    suffix = _suffix_for_mime(audio_mime)
    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        path = Path(tmp.name)
    try:
        return speech_to_text(path)
    finally:
        path.unlink(missing_ok=True)


def speech_to_text(audio_path: str | Path) -> str:
    from vosk import KaldiRecognizer, Model

    source_path = Path(audio_path)
    wav_path = _ensure_wav(source_path)
    model = Model(str(settings.VOSK_MODEL_DIR))
    recognizer = KaldiRecognizer(model, 16000)
    chunks: list[str] = []

    with wave.open(str(wav_path), "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if recognizer.AcceptWaveform(data):
                chunks.append(json.loads(recognizer.Result()).get("text", ""))
        chunks.append(json.loads(recognizer.FinalResult()).get("text", ""))

    if wav_path != source_path:
        wav_path.unlink(missing_ok=True)
    return " ".join(chunk for chunk in chunks if chunk).strip()


def _ensure_wav(path: Path) -> Path:
    from pydub import AudioSegment

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = Path(tmp.name)

    AudioSegment.from_file(path).set_frame_rate(16000).set_channels(1).set_sample_width(2).export(
        wav_path,
        format="wav",
    )
    return wav_path


def _suffix_for_mime(audio_mime: str | None) -> str:
    normalized_mime = (audio_mime or "").split(";")[0].strip().lower()
    if normalized_mime in {"audio/wav", "audio/wave", "audio/x-wav"}:
        return ".wav"
    if normalized_mime == "audio/webm":
        return ".webm"
    if normalized_mime in {"audio/mp3", "audio/mpeg"}:
        return ".mp3"
    return ".mp3"
