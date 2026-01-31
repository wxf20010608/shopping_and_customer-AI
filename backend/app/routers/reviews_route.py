"""
商品评价路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/products/{product_id}/users/{user_id}", response_model=schemas.ReviewRead, status_code=201)
def create_review(
    product_id: int,
    user_id: int,
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    """创建商品评价"""
    return review_service.create_review(user_id, product_id, payload, db)


@router.get("/products/{product_id}", response_model=schemas.ReviewPage)
def list_product_reviews(
    product_id: int,
    status: Optional[str] = Query("approved", description="评价状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取商品评价列表"""
    return review_service.list_reviews(product_id=product_id, status=status, page=page, page_size=page_size, db=db)


@router.get("/products/{product_id}/stats", response_model=schemas.ProductReviewStats)
def get_product_review_stats(product_id: int, db: Session = Depends(get_db)):
    """获取商品评价统计"""
    stats = review_service.get_product_review_stats(product_id, db)
    return schemas.ProductReviewStats(**stats)


@router.get("/users/{user_id}", response_model=schemas.ReviewPage)
def list_user_reviews(
    user_id: int,
    status: Optional[str] = Query(None, description="评价状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取用户的评价列表"""
    return review_service.list_reviews(user_id=user_id, status=status, page=page, page_size=page_size, db=db)


@router.get("/{review_id}", response_model=schemas.ReviewRead)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """获取单个评价"""
    return review_service.get_review(review_id, db)


@router.put("/{review_id}/users/{user_id}", response_model=schemas.ReviewRead)
def update_review(
    review_id: int,
    user_id: int,
    payload: schemas.ReviewUpdate,
    db: Session = Depends(get_db)
):
    """更新评价（只能更新自己的评价）"""
    return review_service.update_review(review_id, user_id, payload, db)


@router.delete("/{review_id}/users/{user_id}")
def delete_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    """删除评价（只能删除自己的评价）"""
    return review_service.delete_review(review_id, user_id, db)
