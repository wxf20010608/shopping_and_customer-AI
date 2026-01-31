from __future__ import annotations

from enum import Enum as PyEnum
from typing import List, TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, Text, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .product_models import Product
    from .shipping_models import ShippingInfo
    from .user_models import User
    from .review_models import Review


class OrderStatusEnum(str, PyEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, PyEnum):
    COD = "cod"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    BANK_CARD = "bank_card"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(Enum(PaymentMethodEnum), nullable=False)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    discount_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    applied_coupon_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deleted_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    shipping: Mapped["ShippingInfo"] = relationship(
        back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(back_populates="order")


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


__all__ = [
    "Order",
    "OrderItem",
    "OrderStatusEnum",
    "PaymentMethodEnum",
]

