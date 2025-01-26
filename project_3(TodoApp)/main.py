from fastapi import FastAPI, Request, status
import models
from database import engine
from routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine) # 创建 models 类中定义的所有模型类对应的表

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def test(request: Request):
    return RedirectResponse(url='/todos/todo-page', status_code=status.HTTP_302_FOUND)

@app.get('/healthy')
def health_check():
    return {'status': 'healthy'}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)