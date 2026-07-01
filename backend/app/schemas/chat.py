from typing import List, Optional

from pydantic import BaseModel


class Citation(BaseModel):
    filename: str
    text: str
    score: float
    document_id: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    citations: List[Citation]


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: int


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: int
    citations: Optional[List[Citation]] = None
