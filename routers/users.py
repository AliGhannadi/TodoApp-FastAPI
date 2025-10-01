# 1. Create a new route called Users.

#2. Then create 2 new API Endpoints

#get_user: this endpoint should return all information about the user that is currently logged in.

# change_password: this endpoint should allow a user to change their current password.
from fastapi import APIRouter, Depends, status, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Annotated
from models import Users, Todos
from db import SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from .auth import get_current_user
from schemas import UpdatePhoneNumber
router = APIRouter(
    prefix='/User',
    tags=['User']
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')    
SECRET_KEY = '28ae950b367f07500992b42c37709ea5ea48c736e2dcc9eaf95ad151aa86f5b7'
ALGORITHM = 'HS256'
@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed.')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail='User Not Found.')

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password_request: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed.')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')
    if bcrypt_context.verify(password_request.old_password, user_model.hashed_password):
        user_model.hashed_password = bcrypt_context.hash(password_request.new_password)
        db.commit()
        return {"message": "Password updated successfully"}
    else:
        raise HTTPException(status_code=401, detail='Error on password change.')
    
@router.put("/update_phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency, request:UpdatePhoneNumber):
    user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not user:
        raise HTTPException(status_code=404, detail='You must authenticate first.')
    user.phone_number = request.phone_number
    db.commit()
    db.refresh(user)
    
@router.put("/update_complete_status/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_complete_status(user: user_dependency, db: db_dependency, todo_id: int = Path(..., gt=0), complete: bool = Query(...)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail='Authentication failed or not authorized.')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found.')
    todo_model.complete = complete
    db.commit()
    db.refresh(todo_model)
    return todo_model