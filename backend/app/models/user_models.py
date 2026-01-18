from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .cart_models import Cart
    from .order_models import Order
    from .address_models import Address
    from .review_models import Review
    from .membership_models import Membership


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False)
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    membership: Mapped["Membership"] = relationship(back_populates="user", uselist=False)
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")


__all__ = ["User"]