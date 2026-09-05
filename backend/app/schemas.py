from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    title: str = "New conversation"


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    sources: list = []
    created_at: datetime


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = []


class ChatRequest(BaseModel):
    session_id: int
    message: str
    provider: str = "ollama"


class Source(BaseModel):
    episode: str
    guest: str
    reference: str
    preview: str
