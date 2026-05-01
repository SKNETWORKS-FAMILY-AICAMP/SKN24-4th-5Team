from pydantic import BaseModel


class AgentRequest(BaseModel):
    user_id: str
    chat_id: str
    question: str