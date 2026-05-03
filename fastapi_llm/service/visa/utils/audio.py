import base64
import tempfile
from pathlib import Path


# Decode base64 audio to a temporary file and analyze speaking features.
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


# Analyze duration, speed, filler usage, pause ratio, and speaking score.
def analyze_audio(audio_path: str | Path, text: str) -> dict:
    try:
        import librosa
    except ImportError:
        return {}

    y, sr = librosa.load(str(audio_path))
    duration = librosa.get_duration(y=y, sr=sr)
    words = text.split()
    speed = len(words) / duration if duration > 0 else 0
    speed_wpm = speed * 60
    fillers = ["um", "uh", "like", "you know"]
    filler_count = sum(text.lower().count(filler) for filler in fillers)
    intervals = librosa.effects.split(y, top_db=20)
    speech_duration = sum((end - start) for start, end in intervals) / sr
    pause_ratio = (duration - speech_duration) / duration if duration > 0 else 0
    speaking_score = calculate_speaking_score(speed_wpm, pause_ratio, filler_count)

    return {
        "duration": round(duration, 2),
        "speed": round(speed, 2),
        "speed_wpm": round(speed_wpm, 2),
        "filler_count": filler_count,
        "pause_ratio": round(pause_ratio, 2),
        **speaking_score,
    }


# Score speaking ability with speed 30, rhythm 30, and fluency 40.
def calculate_speaking_score(speed_wpm: float, pause_ratio: float, filler_count: int) -> dict:
    speed_score = _score_speed(speed_wpm)
    rhythm_score = _score_rhythm(pause_ratio)
    fluency_score = 40 - (filler_count * 2) - (pause_ratio * 10)
    fluency_score = max(0, min(40, fluency_score))
    speaking_score_100 = speed_score + rhythm_score + fluency_score

    return {
        "speed_score": round(speed_score, 2),
        "rhythm_score": round(rhythm_score, 2),
        "fluency_score": round(fluency_score, 2),
        "speaking_score_100": round(speaking_score_100, 2),
        "speaking_score_25": round(speaking_score_100 * 0.25, 2),
    }


# Convert WPM into the 30-point speed score.
def _score_speed(speed_wpm: float) -> int:
    if 90 <= speed_wpm <= 150:
        return 30
    if 70 <= speed_wpm < 90 or 150 < speed_wpm <= 170:
        return 20
    if 60 <= speed_wpm < 70 or 170 < speed_wpm <= 190:
        return 10
    return 5


# Convert pause ratio into the 30-point rhythm score.
def _score_rhythm(pause_ratio: float) -> int:
    if 0.10 <= pause_ratio <= 0.25:
        return 30
    if 0.25 < pause_ratio <= 0.40:
        return 20
    if 0.05 <= pause_ratio < 0.10:
        return 10
    return 5
