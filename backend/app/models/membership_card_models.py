from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .membership_plan_models import MembershipPlan


class MembershipCard(Base, TimestampMixin):
    __tablename__ = "membership_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("membership_plans.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="unassigned")
    published: Mapped[bool] = mapped_column(Boolean, default=False)

    plan: Mapped["MembershipPlan"] = relationship()


__all__ = ["MembershipCard"]