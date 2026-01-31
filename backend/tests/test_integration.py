"""
集成测试
"""
import pytest
from fastapi import status


def test_api_health(client):
    """测试API健康检查"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


def test_product_list_api(client):
    """测试商品列表API"""
    response = client.get("/api/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_user_registration_flow(client):
    """测试用户注册流程"""
    # 注册用户
    register_response = client.post("/api/users/register", json={
        "username": "apitestuser",
        "email": "apitest@example.com",
        "password": "testpass123",
        "full_name": "API Test User"
    })
    assert register_response.status_code == status.HTTP_201_CREATED
    
    user_data = register_response.json()
    assert user_data["username"] == "apitestuser"
    assert "id" in user_data
    
    # 登录用户
    login_response = client.post("/api/users/login", json={
        "identity": "apitestuser",
        "password": "testpass123"
    })
    assert login_response.status_code == status.HTTP_200_OK
