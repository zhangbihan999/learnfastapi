from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from starlette import status  # 定制化状态码返回内容
from requests.TodoRequest import TodoRequest
from .auth import get_current_user
from database import get_db

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependency = Annotated[Session, Depends(get_db)] # Depends(get_db)，注入依赖，每次执行下面的方法体时都会首先执行 get_db() 方法
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todos).all()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()