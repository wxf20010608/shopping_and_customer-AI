from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .user_models import User
    from .membership_plan_models import MembershipPlan


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    level: Mapped[str] = mapped_column(String(50), default="standard")
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("membership_plans.id"), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    extra_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="membership")
    plan: Mapped["MembershipPlan"] = relationship(back_populates="memberships")


__all__ = ["Membership"]