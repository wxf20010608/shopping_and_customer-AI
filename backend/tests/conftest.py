"""
pytest 配置和公共 fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import create_app


# 测试数据库（内存数据库）
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    from app.models import User
    from app.utils import hash_password
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_product(db):
    """创建测试商品"""
    from app.models import Product
    
    product = Product(
        name="Test Product",
        description="Test Description",
        price=99.99,
        stock=100,
        category="测试分类"
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
