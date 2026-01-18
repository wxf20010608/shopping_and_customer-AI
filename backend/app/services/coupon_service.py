from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from ..models import Coupon, UserCoupon, DiscountType, User
from .. import schemas


def list_coupons(db: Session) -> list[Coupon]:
    return db.query(Coupon).order_by(Coupon.created_at.desc()).all()


def create_coupon(payload: schemas.CouponCreate, db: Session) -> Coupon:
    if db.query(Coupon.id).filter(Coupon.code == payload.code).first():
        raise HTTPException(status_code=400, detail="优惠券编码已存在")
    c = Coupon(**payload.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c


def update_coupon(coupon_id: int, payload: schemas.CouponUpdate, db: Session) -> Coupon:
    c = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c


def delete_coupon(coupon_id: int, db: Session):
    c = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    db.delete(c); db.commit()
    return {"deleted": True}


def assign_coupon_to_user(coupon_id: int, user_id: int, db: Session) -> UserCoupon:
    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="用户不存在")
    c = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not c or not c.active:
        raise HTTPException(status_code=400, detail="优惠券不可用")
    uc = UserCoupon(user_id=user_id, coupon_id=coupon_id, status="unused")
    db.add(uc); db.commit(); db.refresh(uc)
    return uc


def list_user_coupons(user_id: int, db: Session) -> list[UserCoupon]:
    u = db.query(User.id).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    return (
        db.query(UserCoupon)
        .options(selectinload(UserCoupon.coupon))
        .filter(UserCoupon.user_id == user_id)
        .order_by(UserCoupon.created_at.desc())
        .all()
    )


def compute_coupon_discount(base_amount: float, uc: UserCoupon, cart_items=None) -> float:
    c = uc.coupon
    now = datetime.utcnow()
    if c.valid_from and now < c.valid_from:
        raise HTTPException(status_code=400, detail="优惠券未到使用期")
    if c.valid_to and now > c.valid_to:
        raise HTTPException(status_code=400, detail="优惠券已过期")
    if not c.active:
        raise HTTPException(status_code=400, detail="优惠券不可用")
    if c.min_spend and base_amount < c.min_spend:
        raise HTTPException(status_code=400, detail="未满足最小消费金额")

    if c.discount_type == DiscountType.AMOUNT:
        return min(base_amount, c.discount_value)
    else:
        # percent，可选按商品限定
        if getattr(c, "allowed_product_id", None) and cart_items is not None:
            sub_amount = 0.0
            for it in cart_items:
                try:
                    pid = it.product_id if hasattr(it, "product_id") else it.product.id
                    price = it.unit_price if hasattr(it, "unit_price") else it.product.price
                    qty = it.quantity
                except Exception:
                    continue
                if pid == c.allowed_product_id:
                    sub_amount += price * qty
            if sub_amount <= 0:
                raise HTTPException(status_code=400, detail="该折扣券不适用于当前商品")
            return round(sub_amount * (c.discount_value / 100.0), 2)
        return round(base_amount * (c.discount_value / 100.0), 2)