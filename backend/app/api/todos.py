from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import SessionLocal
from ..models.user import User
from ..models.todo import Todo
from ..schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from ..deps import get_current_user

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[TodoResponse])
def list_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    items = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(
        Todo.completed.asc(),
        Todo.priority.desc(),
        Todo.created_at.desc(),
    ).all()
    return items


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    todo = Todo(user_id=current_user.id, **data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    if "completed" in update_data:
        if update_data["completed"] and not todo.completed_at:
            todo.completed_at = datetime.utcnow()
        elif not update_data["completed"]:
            todo.completed_at = None

    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    db.delete(todo)
    db.commit()
    return {"ok": True}
