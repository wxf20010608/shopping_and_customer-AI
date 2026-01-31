"""
用户服务单元测试
"""
import pytest
from fastapi import HTTPException

from app.services import user_service
from app import schemas


def test_register_user(db):
    """测试用户注册"""
    payload = schemas.UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="password123",
        full_name="New User"
    )
    user = user_service.register_user(payload, db)
    
    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"


def test_register_duplicate_username(db, test_user):
    """测试重复用户名注册"""
    payload = schemas.UserCreate(
        username="testuser",
        email="another@example.com",
        password="password123"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(payload, db)
    assert exc_info.value.status_code == 400


def test_login_user(db, test_user):
    """测试用户登录"""
    payload = schemas.UserLogin(
        identity="testuser",
        password="testpass123"
    )
    user = user_service.login_user(payload, db)
    
    assert user.id == test_user.id
    assert user.username == test_user.username


def test_login_wrong_password(db, test_user):
    """测试错误密码登录"""
    payload = schemas.UserLogin(
        identity="testuser",
        password="wrongpassword"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.login_user(payload, db)
    assert exc_info.value.status_code == 401
