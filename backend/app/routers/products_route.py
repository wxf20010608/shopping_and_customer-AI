from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import product_service

router = APIRouter(prefix="/products", tags=["products"]) 


@router.post("/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(payload, db)


@router.get("/", response_model=schemas.ProductPage)
def list_products(
    search: Optional[str] = Query(default=None, description="按商品名称或分类搜索"),
    category: Optional[str] = Query(default=None, description="按分类精确筛选"),
    page: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    random_order: bool = Query(default=True, description="是否随机排序（默认True，每次刷新顺序不同）"),
    db: Session = Depends(get_db),
):
    return product_service.list_products(search, category, db, page, page_size, random_order)


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    return product_service.list_categories(db)


@router.get("/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(product_id, db)


@router.get("/{product_id}/customer-service", response_model=schemas.CustomerServiceResponse)
def get_product_customer_service(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_customer_service(product_id, db)


# 已停用：批量生成商品接口
# @router.post("/seed", response_model=List[schemas.ProductRead])
# def seed_products(count: int = Query(default=50, ge=1, le=1000, description="生成商品数量"), db: Session = Depends(get_db)):
#     return product_service.seed_products(count, db)

