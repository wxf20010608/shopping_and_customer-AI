from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_

from .. import schemas
from ..models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatusEnum,
    PaymentMethodEnum,
    Product,
    ShippingInfo,
    ShippingStatusEnum,
    User,
    Membership,
    MembershipPlan,
    UserCoupon,
)
from .membership_service import get as get_membership
from .coupon_service import compute_coupon_discount


def _load_user_with_cart(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            selectinload(User.cart)
            .selectinload(Cart.items)
            .selectinload(CartItem.product)
        )
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(user)
    return user


def create_order(user_id: int, payload: schemas.OrderCreate, db: Session) -> Order:
    try:
        payment_method = (
            payload.payment_method
            if isinstance(payload.payment_method, PaymentMethodEnum)
            else PaymentMethodEnum(str(payload.payment_method))
        )
    except Exception:
        raise HTTPException(status_code=400, detail="支付方式不支持")

    if not (payload.shipping_address and payload.shipping_address.strip()):
        raise HTTPException(status_code=400, detail="收货地址不能为空")
    if not (payload.shipping_carrier and payload.shipping_carrier.strip()):
        raise HTTPException(status_code=400, detail="物流公司不能为空")

    user = _load_user_with_cart(db, user_id)
    cart = user.cart
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="购物车为空，无法下单")

    total_amount = 0.0
    for item in cart.items:
        total_amount += item.product.price * item.quantity

    # 折扣与会员余额处理
    discount = 0.0
    use_membership = bool(getattr(payload, "use_membership", False))
    coupon_id = getattr(payload, "coupon_id", None)

    if use_membership and coupon_id:
        raise HTTPException(status_code=400, detail="会员与优惠券不可同时使用")

    payable_amount = total_amount
    used_user_coupon: UserCoupon | None = None

    applied_coupon_id: int | None = None
    discount_type: str | None = None

    if coupon_id:
        uc = (
            db.query(UserCoupon)
            .options(selectinload(UserCoupon.coupon))
            .filter(UserCoupon.id == coupon_id, UserCoupon.user_id == user.id)
            .first()
        )
        if not uc:
            raise HTTPException(status_code=404, detail="优惠券不存在")
        if uc.status != "unused":
            raise HTTPException(status_code=400, detail="优惠券已使用或不可用")
        discount = compute_coupon_discount(total_amount, uc, cart_items=cart.items)
        payable_amount = max(0.0, total_amount - discount)
        used_user_coupon = uc
        applied_coupon_id = uc.coupon_id
        discount_type = "coupon"

    if use_membership:
        m = get_membership(db, user.id)
        if not m:
            raise HTTPException(status_code=404, detail="会员不存在")
        if m.status != "active":
            raise HTTPException(status_code=400, detail="会员不可用")
        # 根据计划折扣（discount_percent 表示折扣百分比，10=>9折；0=>无折扣）
        percent = 10.0
        if m.plan_id:
            plan = db.query(MembershipPlan).filter(MembershipPlan.id == m.plan_id, MembershipPlan.active == True).first()
            if plan:
                percent = plan.discount_percent or 0
        payable_amount = round(total_amount * (1 - percent/100.0), 2)
        if m.balance < payable_amount:
            raise HTTPException(status_code=400, detail="会员余额不足，请先充值")
        m.balance -= payable_amount
        db.add(m)
        discount = round(total_amount - payable_amount, 2)
        discount_type = "membership"

    order = Order(
        user_id=user.id,
        status=OrderStatusEnum.PAID if payment_method != PaymentMethodEnum.COD else OrderStatusEnum.PENDING,
        total_amount=payable_amount,
        payment_method=payment_method,
        shipping_address=payload.shipping_address,
        discount_type=discount_type,
        discount_amount=discount,
        applied_coupon_id=applied_coupon_id,
    )
    db.add(order)
    db.flush()

    order_items: List[OrderItem] = []
    for item in cart.items:
        order_items.append(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
        )
    db.add_all(order_items)

    shipping = ShippingInfo(
        order_id=order.id,
        carrier=payload.shipping_carrier,
        tracking_number=payload.tracking_number,
        status=ShippingStatusEnum.CREATED,
        estimated_delivery=datetime.utcnow() + timedelta(days=3),
    )
    db.add(shipping)

    for item in list(cart.items):
        db.delete(item)

    db.commit()
    
    # 标记优惠券使用
    if used_user_coupon:
        used_user_coupon.status = "used"
        used_user_coupon.used_order_id = order.id
        db.add(used_user_coupon)
        db.commit()
    return (
        db.query(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.shipping),
        )
        .filter(Order.id == order.id)
        .first()
    )


def list_orders(user_id: int, db: Session) -> List[Order]:
    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="用户不存在")

    orders = (
        db.query(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.shipping),
        )
        .filter(
            Order.user_id == user_id,
            or_(Order.deleted_by_user == False, Order.deleted_by_user.is_(None))
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders


def get_order(order_id: int, db: Session) -> Order:
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.shipping),
        )
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.deleted_by_user:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


def delete_order(user_id: int, order_id: int, db: Session) -> dict:
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if getattr(order, 'deleted_by_user', False):
        return {"deleted": True}
    from datetime import datetime
    if hasattr(order, 'deleted_by_user'):
        order.deleted_by_user = True
    if hasattr(order, 'deleted_at'):
        order.deleted_at = datetime.utcnow()
    db.add(order)
    db.commit()
    return {"deleted": True}

