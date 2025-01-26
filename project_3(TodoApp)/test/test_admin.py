from .utils import *
from main import app
from database import get_db
from routers.auth import get_current_user
from fastapi.testclient import TestClient
from fastapi import status
from models import Todos

app.dependency_overrides[get_db] = override_get_db  # 当 app 尝试使用 get_db 进行依赖注入时，改为使用 override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_admin_read_all_authenticated(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'learn to code', 'owner_id': 1, 'complete': False, 'priority': 5, 'description': 'need to do everyday', 'id': 1}]

def test_admin_delete_todo(test_todo):
    reponse = client.delete('/admin/todo/1')
    assert reponse.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/admin/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response.json() == []
    
