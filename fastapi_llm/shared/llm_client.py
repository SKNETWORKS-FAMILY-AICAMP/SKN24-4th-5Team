from functools import lru_cache

from fastapi_llm.service.visa.config.settings import settings


# 
class SimpleLLMClient:
    def __init__(self, model: str | None = None, temperature: float | None = None):
        self.model = model or settings.OLLAMA_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self._client = None

    # 
    def _load_client(self):
        if self._client is None:
            from langchain_ollama import ChatOllama

            self._client = ChatOllama(model=self.model, temperature=self.temperature)
        return self._client

    #
    def invoke(self, prompt: str) -> str:
        response = self._load_client().invoke(prompt)
        return getattr(response, "content", str(response)).strip()


#
@lru_cache(maxsize=1)
def get_llm_client() -> SimpleLLMClient:
    return SimpleLLMClient()

