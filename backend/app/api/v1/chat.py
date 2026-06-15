from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import User
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse, SessionResponse
from app.services import history as history_svc
from app.services import access as access_svc
from app.services.rag import rag_query

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = str(current_user.id)

    if req.session_id:
        sessions = history_svc.list_sessions(db, user_id)
        if req.session_id not in [s["session_id"] for s in sessions]:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = req.session_id
    else:
        session_id = history_svc.create_session(db, user_id, title=req.message[:60])

    history = history_svc.get_messages(db, session_id)
    allowed_doc_ids = access_svc.get_accessible_doc_ids(current_user, db)
    answer, citations = rag_query(req.message, history, allowed_doc_ids=allowed_doc_ids)

    history_svc.add_message(db, session_id, "user", req.message)
    history_svc.add_message(db, session_id, "assistant", answer, citations)

    if not history:
        history_svc.update_session_title(db, session_id, req.message[:60])

    return ChatResponse(session_id=session_id, message=answer, citations=citations)


@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return history_svc.list_sessions(db, str(current_user.id))


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = history_svc.list_sessions(db, str(current_user.id))
    if session_id not in [s["session_id"] for s in sessions]:
        raise HTTPException(status_code=404, detail="Session not found")
    return history_svc.get_messages(db, session_id)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        history_svc.delete_session(db, session_id, str(current_user.id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
