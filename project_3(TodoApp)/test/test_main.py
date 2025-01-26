from fastapi.testclient import TestClient
from main import app
from fastapi import status

client = TestClient(app)  # TestClient 实例能够模拟 fastapi 应用发送 http 请求

def test_health_check():
    response = client.get("/healthy")  # 模拟向 /healthy 路由发送一个 get 请求
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'healthy'}