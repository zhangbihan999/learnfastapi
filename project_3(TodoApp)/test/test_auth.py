from datetime import timedelta

from fastapi import HTTPException
from .utils import *
from fastapi.testclient import TestClient
from database import get_db
from main import app
from routers.auth import authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
import pytest

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user("wrong_username", "testpassword", db)
    assert non_existent_user == False

    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user == False

def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'admin'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'