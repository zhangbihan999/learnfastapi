from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from typing import Annotated
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from starlette import status  # 定制化状态码返回内容
from requests.TodoRequest import TodoRequest
from .auth import get_current_user
from database import get_db
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

db_dependency = Annotated[Session, Depends(get_db)] # Depends(get_db)，注入依赖，每次执行下面的方法体时都会首先执行 get_db() 方法
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="templates")

def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

### Pages ###
@router.get('/todo-page')
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()

@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()

### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, 
                   db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, 
                    db: db_dependency, 
                    todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, 
                      db: db_dependency, 
                      todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model) # 将创建的 Todos 实例添加到当前的数据库会话中
    db.commit() # 提交数据库事务，即，将更改持久化的数据库中

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, 
                      db: db_dependency, 
                      todo_request: TodoRequest, 
                      todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, 
                      db: db_dependency, 
                      todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).\
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).delete()

    db.commit()