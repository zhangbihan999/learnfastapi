from main import app
from database import get_db
from routers.auth import get_current_user
from fastapi.testclient import TestClient
from fastapi import status
from models import Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db  # 当 app 尝试使用 get_db 进行依赖注入时，改为使用 override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'learn to code', 'owner_id': 1, 'complete': False, 'priority': 5, 'description': 'need to do everyday', 'id': 1}]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'learn to code', 'owner_id': 1, 'complete': False, 'priority': 5, 'description': 'need to do everyday', 'id': 1}

def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todos/todos/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'new todo',
        'description': 'new todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todos/todo', json=request_data)
    
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todo):
    request_data = {
        'title': 'update todo',
        'description': 'null',
        'priority': 5,
        'complete': False
    }

    response = client.put('/todos/todos/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == 'update todo'

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'update todo',
        'description': 'null',
        'priority': 5,
        'complete': False
    }

    response = client.put('/todos/todos/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}

def test_delete_todo(test_todo):
    response = client.delete('/todos/todos/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete('/todos/todos/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}
