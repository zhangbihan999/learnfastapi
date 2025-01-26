from .utils import *
from main import app
from database import get_db
from routers.auth import get_current_user
from fastapi.testclient import TestClient
from fastapi import status

app.dependency_overrides[get_db] = override_get_db  # 当 app 尝试使用 get_db 进行依赖注入时，改为使用 override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_get_user(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('username') == 'zc'

def test_change_password(test_user):
    response = client.put('/user/password', json={'password': 'testpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_user):
    response = client.put('/user/password', json={'password': 'wrongpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': '密码不正确'}

def test_change_phone_number(test_user):
    response = client.put('/user/phone-number/12345')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == '12345'