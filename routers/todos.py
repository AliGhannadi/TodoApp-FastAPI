from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session 
from typing import Annotated
from models import Todos, Users
from db import SessionLocal
from .auth import get_current_user
from schemas import TodoRequest
from emails import schedule_email



router = APIRouter(
    prefix='',
    tags=['Todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

#######################################
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo Not Found.')


@router.post("/todo/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, todo_request: TodoRequest, db: db_dependency):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user_model or user is None:
        raise HTTPException(status_code=404, detail="Authentication Failed.")
    todo_model = Todos(
        **todo_request.model_dump(exclude={"owner_id"}),
        owner_id=user_model.id
    )
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)    
    schedule_email(
        email=user_model.email,
        subject='Todo Reminder',
        message=f"Your todo must be done now: Title: {todo_model.title}، Description: '{todo_model.description}' ",
        scheduled_time=todo_model.scheduled_time        
    )
    return todo_model

@router.put("/todo/update_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found.')
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()

@router.delete("/todo/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found.')
    db.delete(todo_model)
    db.commit()
    return None


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

