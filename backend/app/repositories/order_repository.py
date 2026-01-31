from typing import List

from sqlalchemy.orm import Session, selectinload

from ..models import Order, OrderItem


def create_order(db: Session, data: dict) -> Order:
    order = Order(**data)
    db.add(order)
    db.flush()
    return order


def create_order_items(db: Session, items: List[dict]) -> List[OrderItem]:
    order_items: List[OrderItem] = []
    for item_data in items:
        order_item = OrderItem(**item_data)
        db.add(order_item)
        order_items.append(order_item)
    db.flush()
    return order_items


def get_orders_by_user(db: Session, user_id: int) -> List[Order]:
    return (
        db.query(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.shipping),
        )
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int) -> Order | None:
    return (
        db.query(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.shipping),
        )
        .filter(Order.id == order_id)
        .first()
    )

