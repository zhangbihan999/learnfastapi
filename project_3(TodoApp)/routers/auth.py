from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from models import Users
from sqlalchemy.orm import Session
from typing import Annotated
from requests.CreateUserRequest import CreateUserRequest
from requests.Token import Token
from starlette import status  # 定制化状态码返回内容
from passlib.context import CryptContext
from database import SessionLocal
# 处理 OAuth 2.0 密码授权中的用户登录请求，自动解析从客户端提交的用户名和密码，并将其封装到 form_data 中
#（自动提供两个字段 username 和 password，并且会自动解析这些字段为一个表单数据对象）
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '62de4e88832a7e681b33ddab416ec7da7e7796b6caea2ae8d7de23cf302786c7'
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)] # Depends(get_db)，注入依赖，每次执行下面的方法体时都会首先执行 get_db() 方法
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

templates = Jinja2Templates(directory="templates")

### Pages ###
@router.get('/login-page')
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get('/register-page')
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

### Endpoints ###
def authenticate_user(username: str, password: str, db):
    """ 
    authentication 即验证给定 username 和 password 是否在数据库中，回答的是“你是谁”的问题。
    authorization 是授权，回答的是“你能做什么”的问题。
    """
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user_model = Users(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    
    db.add(user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}