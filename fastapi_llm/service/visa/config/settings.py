"""프로젝트 전역 설정"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==== 경로 설정 ===========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# STT 모델 경로
STT_MODEL_PATH = os.path.join(BASE_DIR, "model_stt", "vosk-model-small-en-us-0.15")

# TTS 모델 경로
TTS_EXE_PATH   = os.path.join(BASE_DIR, "model_tts", "piper", "piper.exe")
TTS_MODEL_PATH = os.path.join(BASE_DIR, "model_tts", "piper", "en_US-lessac-medium.onnx")

# 폰트 경로
FONT_PATH = os.path.join(BASE_DIR, "fonts", "NanumGothic.ttf")

# ChromaDB 저장 경로
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")

# ====LLM 설정 ===========================
LLM_MODEL      = "ebdm/gemma3-enhanced:12b"
LLM_TEMPERATURE = 0.5

# ==== Embedding 설정====================
EMBED_MODEL_NAME   = "BAAI/bge-m3"
EMBED_DEVICE       = "cpu"          # GPU 사용 시 "cuda"

# ==== ChromaDB 설정 ===========================
CHROMA_COLLECTION  = "s2_interview_data"

# ==== 인터뷰 설정 ===========================
REAL_MODE_TIMER_SEC = 420           # 실전모드 타이머 (7분)
AUTO_START_DELAY_SEC = 5            # 실전모드 자동 녹음 대기 시간

# ==== 음성 녹음 설정 ===========================
AUDIO_SAMPLE_RATE = 16000           # Hz
AUDIO_CHANNELS    = 1
AUDIO_FILENAME    = "speech.wav"

# ==== PDF 설정 ===========================
MAX_PDF_SIZE_MB   = 5
