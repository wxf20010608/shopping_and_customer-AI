"""
商品服务单元测试
"""
import pytest
from fastapi import status

from app.services import product_service
from app import schemas


def test_create_product(db):
    """测试创建商品"""
    payload = schemas.ProductCreate(
        name="Test Product",
        description="Test Description",
        price=99.99,
        stock=100,
        category="测试分类"
    )
    product = product_service.create_product(payload, db)
    
    assert product.id is not None
    assert product.name == "Test Product"
    assert product.price == 99.99
    assert product.stock == 100


def test_get_product(db, test_product):
    """测试获取商品"""
    product = product_service.get_product(test_product.id, db)
    assert product.id == test_product.id
    assert product.name == test_product.name


def test_list_products(db, test_product):
    """测试商品列表"""
    result = product_service.list_products(None, None, db, page=1, page_size=10)
    assert result.total >= 1
    assert len(result.items) >= 1


def test_list_categories(db):
    """测试获取分类列表"""
    categories = product_service.list_categories(db)
    assert isinstance(categories, list)
