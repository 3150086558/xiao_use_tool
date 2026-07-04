from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import SessionLocal
from ..models.user import User
from ..models.note import Note
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse
from ..deps import get_current_user

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[NoteResponse])
def list_notes(
    keyword: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    query = db.query(Note).filter(Note.user_id == current_user.id)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter((Note.title.like(kw)) | (Note.content.like(kw)))
    items = query.order_by(Note.updated_at.desc()).all()
    return items


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    note = Note(user_id=current_user.id, **data.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    note = db.query(Note).filter(
        Note.id == note_id, Note.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="备忘录不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    note = db.query(Note).filter(
        Note.id == note_id, Note.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="备忘录不存在")
    db.delete(note)
    db.commit()
    return {"ok": True}
