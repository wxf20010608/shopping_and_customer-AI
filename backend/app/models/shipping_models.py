from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .order_models import Order


class ShippingStatusEnum(str, PyEnum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class ShippingInfo(Base, TimestampMixin):
    __tablename__ = "shipping_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    carrier: Mapped[str] = mapped_column(String(100), nullable=False)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ShippingStatusEnum), default=ShippingStatusEnum.CREATED
    )
    estimated_delivery: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="shipping")


__all__ = ["ShippingInfo", "ShippingStatusEnum"]