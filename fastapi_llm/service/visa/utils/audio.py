"""
utils/audio.py
──────────────
음성 녹음(record) + 음성 분석(analyze_audio) 유틸리티
"""

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import librosa

from config.settings import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_FILENAME


# ── 녹음 ─────────────────────────────────────────────────────────────────────

def record(filename: str = AUDIO_FILENAME,
           fs: int = AUDIO_SAMPLE_RATE,
           auto_start: bool = False) -> None:
    """
    마이크에서 오디오를 녹음하고 WAV 파일로 저장합니다.

    Parameters
    ----------
    filename    : 저장할 WAV 파일 경로
    fs          : 샘플링 레이트 (기본 16000 Hz)
    auto_start  : True 이면 Enter 없이 자동 시작, False 이면 Enter 후 시작
    """
    print("녹음 준비...")

    recording = []

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    stream = sd.InputStream(samplerate=fs, channels=AUDIO_CHANNELS, callback=callback)

    if not auto_start:
        input("Enter 누르면 녹음 시작")

    stream.start()

    if auto_start:
        print("자동 녹음 시작 (Enter로 종료)")
    else:
        print("녹음 중... (Enter 누르면 종료)")

    input()  # 종료 대기

    stream.stop()
    stream.close()

    audio = np.concatenate(recording, axis=0)
    audio = (audio * 32767).astype(np.int16)   # VOSK 필수: int16 변환

    write(filename, fs, audio)
    print("녹음 완료")


# ── 음성 분석 ─────────────────────────────────────────────────────────────────

def analyze_audio(audio_path: str, text: str) -> dict:
    """
    librosa 기반 음성 분석.

    Returns
    -------
    dict
        duration        : 전체 길이 (초)
        word_count      : 단어 수
        speed           : 말 속도 (words/sec)
        filler_count    : 추임새 횟수
        energy          : 평균 RMS 에너지 (자신감 지표)
        pause_duration  : 침묵 총 길이 (초)
        pause_ratio     : 침묵 비율 (0~1)
    """
    y, sr = librosa.load(audio_path)

    duration   = librosa.get_duration(y=y, sr=sr)
    words      = text.split()
    word_count = len(words)
    speed      = word_count / duration if duration > 0 else 0

    fillers      = ["um", "uh", "like", "you know"]
    filler_count = sum(text.lower().count(f) for f in fillers)

    energy = np.mean(librosa.feature.rms(y=y))

    intervals        = librosa.effects.split(y, top_db=20)
    speech_duration  = sum((end - start) for start, end in intervals) / sr
    pause_duration   = duration - speech_duration
    pause_ratio      = pause_duration / duration if duration > 0 else 0

    return {
        "duration"      : round(duration, 2),
        "word_count"    : word_count,
        "speed"         : round(speed, 2),
        "filler_count"  : filler_count,
        "energy"        : round(float(energy), 4),
        "pause_duration": round(pause_duration, 2),
        "pause_ratio"   : round(pause_ratio, 2),
    }
