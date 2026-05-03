from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings used by the visa interview service.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OLLAMA_MODEL: str = "ebdm/gemma3-enhanced:12b"
    LLM_TEMPERATURE: float = 0.5
    INTERVIEW_DURATION_SECONDS: int = 7 * 60
    MAX_REPLAY: int = 1

    BASE_DIR: Path = Path(__file__).resolve().parents[3]
    VISA_DIR: Path = BASE_DIR / "service" / "visa"
    CHROMA_DIR: Path = VISA_DIR / "chroma_db"
    CHROMA_COLLECTION: str = "s2_interview_data"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    HF_VISA_DATASET: str = "Blessing988/f1_visa_transcripts"
    VOSK_MODEL_DIR: Path = VISA_DIR / "model_stt" / "vosk-model-small-en-us-0.15"


settings = Settings()
