from __future__ import annotations

from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin


class DiscountType(str, PyEnum):
    AMOUNT = "amount"
    PERCENT = "percent"


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    discount_type: Mapped[str] = mapped_column(Enum(DiscountType), default=DiscountType.AMOUNT)
    discount_value: Mapped[float] = mapped_column(Float, default=0.0)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    min_spend: Mapped[float] = mapped_column(Float, default=0.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user_coupons: Mapped[list["UserCoupon"]] = relationship(back_populates="coupon")


class UserCoupon(Base, TimestampMixin):
    __tablename__ = "user_coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"))
    status: Mapped[str] = mapped_column(String(20), default="unused")
    used_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    coupon: Mapped[Coupon] = relationship(back_populates="user_coupons")


__all__ = ["Coupon", "UserCoupon", "DiscountType"]