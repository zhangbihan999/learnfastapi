from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos, Users
from database import SessionLocal
from starlette import status  # 定制化状态码返回内容
from requests.TodoRequest import TodoRequest
from .auth import get_current_user
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from database import get_db

router = APIRouter(
    prefix='/user',
    tags=['user']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)] # Depends(get_db)，注入依赖，每次执行下面的方法体时都会首先执行 get_db() 方法
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=3)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.query(Users).filter(Users.id == user.get('id')).first()
    return user

@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, 
                          db: db_dependency,
                          user_verification: UserVerification):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="密码不正确")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()

@router.put('/phone-number/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()