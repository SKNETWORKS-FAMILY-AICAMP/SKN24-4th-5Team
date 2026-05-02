import base64
import tempfile
from pathlib import Path


# base64 음성 데이터를 임시 파일로 저장한 뒤 말하기 속도와 침묵 비율을 분석
def analyze_audio_base64(audio_base64: str, text: str, audio_mime: str | None = None) -> dict:
    normalized_mime = (audio_mime or "").split(";")[0].strip().lower()
    if normalized_mime in {"audio/wav", "audio/wave", "audio/x-wav"}:
        suffix = ".wav"
    elif normalized_mime == "audio/webm":
        suffix = ".webm"
    else:
        suffix = ".mp3"
    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        path = Path(tmp.name)
    try:
        return analyze_audio(path, text)
    finally:
        path.unlink(missing_ok=True)


# librosa로 답변 음성의 길이, 속도, filler, pause ratio를 계산
def analyze_audio(audio_path: str | Path, text: str) -> dict:
    try:
        import librosa
    except ImportError:
        return {}

    y, sr = librosa.load(str(audio_path))
    duration = librosa.get_duration(y=y, sr=sr)
    words = text.split()
    speed = len(words) / duration if duration > 0 else 0
    fillers = ["um", "uh", "like", "you know"]
    filler_count = sum(text.lower().count(filler) for filler in fillers)
    intervals = librosa.effects.split(y, top_db=20)
    speech_duration = sum((end - start) for start, end in intervals) / sr
    pause_ratio = (duration - speech_duration) / duration if duration > 0 else 0
    return {
        "duration": round(duration, 2),
        "speed": round(speed, 2),
        "filler_count": filler_count,
        "pause_ratio": round(pause_ratio, 2),
    }
