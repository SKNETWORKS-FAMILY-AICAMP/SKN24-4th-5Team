import base64
import tempfile
from pathlib import Path


# gTTS로 생성한 음성 파일을 장고가 받기 쉬운 base64 문자열로 반환
def text_to_speech_base64(text: str) -> str:
    audio_path = text_to_speech(text)
    try:
        return base64.b64encode(audio_path.read_bytes()).decode("ascii")
    finally:
        audio_path.unlink(missing_ok=True)


# gTTS를 호출해 질문 텍스트를 mp3 음성 파일로 생성
def text_to_speech(text: str) -> Path:
    from gtts import gTTS

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = Path(tmp.name)

    tts = gTTS(text=text, lang="en")
    tts.save(str(output_path))
    return output_path
