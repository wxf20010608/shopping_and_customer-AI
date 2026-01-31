from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Order, OrderStatusEnum, ShippingInfo, ShippingStatusEnum


def get_shipping_info(order_id: int, db: Session) -> ShippingInfo:
    shipping = db.query(ShippingInfo).filter(ShippingInfo.order_id == order_id).first()
    if not shipping:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return shipping


def update_shipping_status(
    order_id: int,
    status_value: ShippingStatusEnum,
    db: Session,
    tracking_number: Optional[str] = None,
) -> ShippingInfo:
    shipping = db.query(ShippingInfo).filter(ShippingInfo.order_id == order_id).first()
    if not shipping:
        raise HTTPException(status_code=404, detail="物流信息不存在")

    if tracking_number:
        shipping.tracking_number = tracking_number
    shipping.status = status_value
    db.commit()
    db.refresh(shipping)

    order = db.query(Order).filter(Order.id == order_id).first()
    if order and status_value == ShippingStatusEnum.DELIVERED:
        order.status = OrderStatusEnum.COMPLETED
        db.commit()
    return shipping

