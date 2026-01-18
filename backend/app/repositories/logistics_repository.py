from sqlalchemy.orm import Session

from ..models import ShippingInfo


def create_shipping_info(db: Session, data: dict) -> ShippingInfo:
    shipping = ShippingInfo(**data)
    db.add(shipping)
    db.flush()
    return shipping


def get_by_order_id(db: Session, order_id: int) -> ShippingInfo | None:
    return db.query(ShippingInfo).filter(ShippingInfo.order_id == order_id).first()




