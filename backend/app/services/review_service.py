"""
商品评价和评分服务
"""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, and_

from ..models import Review, Product, Order, OrderItem, User
from .. import schemas


def create_review(user_id: int, product_id: int, payload: schemas.ReviewCreate, db: Session) -> Review:
    """创建商品评价"""
    # 检查商品是否存在
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 验证评分范围
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")
    
    # 检查是否已评价（可选，允许用户多次评价）
    # existing = db.query(Review).filter(
    #     Review.user_id == user_id,
    #     Review.product_id == product_id
    # ).first()
    # if existing:
    #     raise HTTPException(status_code=400, detail="您已经评价过该商品")
    
    # 检查是否为已验证购买（如果提供了订单ID）
    verified_purchase = False
    if payload.order_id:
        order = db.query(Order).filter(
            Order.id == payload.order_id,
            Order.user_id == user_id,
            Order.status == "completed"
        ).first()
        if order:
            # 检查订单中是否包含该商品
            order_item = db.query(OrderItem).filter(
                OrderItem.order_id == order.id,
                OrderItem.product_id == product_id
            ).first()
            if order_item:
                verified_purchase = True
    
    # 处理图片（JSON数组字符串）
    images_json = None
    if payload.images:
        import json
        images_json = json.dumps(payload.images)
    
    review = Review(
        user_id=user_id,
        product_id=product_id,
        order_id=payload.order_id,
        rating=payload.rating,
        comment=payload.comment,
        images=images_json,
        verified_purchase=verified_purchase,
        status="approved"  # 默认自动通过，也可以改为 "pending" 需要审核
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # 更新商品平均评分
    _update_product_rating(product_id, db)
    
    return review


def list_reviews(product_id: Optional[int] = None, user_id: Optional[int] = None,
                 status: Optional[str] = "approved", page: int = 1, page_size: int = 10,
                 db: Session = None) -> schemas.ReviewPage:
    """获取评价列表"""
    query = db.query(Review)
    
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    if status:
        query = query.filter(Review.status == status)
    
    total = query.count()
    items = (
        query.options(selectinload(Review.user), selectinload(Review.product))
        .order_by(Review.created_at.desc())
        .offset((max(page, 1) - 1) * max(page_size, 1))
        .limit(max(page_size, 1))
        .all()
    )
    
    # 解析图片JSON
    for item in items:
        if item.images:
            import json
            try:
                item.images_list = json.loads(item.images)
            except:
                item.images_list = []
        else:
            item.images_list = []
    
    return schemas.ReviewPage(items=items, total=total, page=max(page, 1), page_size=max(page_size, 1))


def get_review(review_id: int, db: Session) -> Review:
    """获取单个评价"""
    review = (
        db.query(Review)
        .options(selectinload(Review.user), selectinload(Review.product))
        .filter(Review.id == review_id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    return review


def update_review(review_id: int, user_id: int, payload: schemas.ReviewUpdate, db: Session) -> Review:
    """更新评价（只能更新自己的评价）"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    
    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="只能修改自己的评价")
    
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        if k == "images" and v:
            import json
            setattr(review, k, json.dumps(v))
        else:
            setattr(review, k, v)
    
    db.commit()
    db.refresh(review)
    
    # 更新商品平均评分
    _update_product_rating(review.product_id, db)
    
    return review


def delete_review(review_id: int, user_id: int, db: Session) -> dict:
    """删除评价（只能删除自己的评价）"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    
    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的评价")
    
    product_id = review.product_id
    db.delete(review)
    db.commit()
    
    # 更新商品平均评分
    _update_product_rating(product_id, db)
    
    return {"deleted": True}


def _update_product_rating(product_id: int, db: Session):
    """更新商品平均评分（可以通过计算字段或额外表字段）"""
    # 计算该商品的平均评分
    result = db.query(func.avg(Review.rating)).filter(
        Review.product_id == product_id,
        Review.status == "approved"
    ).scalar()
    
    avg_rating = round(result, 2) if result else None
    
    # 这里可以更新商品表的 rating 字段（如果存在）
    # 或者在查询时动态计算（当前方案）
    # 如果需要，可以添加 product.rating 字段并在这里更新


def get_product_review_stats(product_id: int, db: Session) -> dict:
    """获取商品评价统计"""
    reviews = db.query(Review).filter(
        Review.product_id == product_id,
        Review.status == "approved"
    ).all()
    
    if not reviews:
        return {
            "avg_rating": 0.0,
            "total_reviews": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    ratings = [r.rating for r in reviews]
    avg_rating = round(sum(ratings) / len(ratings), 2)
    
    rating_distribution = {i: 0 for i in range(1, 6)}
    for rating in ratings:
        rating_distribution[int(rating)] += 1
    
    return {
        "avg_rating": avg_rating,
        "total_reviews": len(reviews),
        "rating_distribution": rating_distribution
    }
