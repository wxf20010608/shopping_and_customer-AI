from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .membership_models import Membership


class MembershipPlan(Base, TimestampMixin):
    __tablename__ = "membership_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    discount_percent: Mapped[float] = mapped_column(Float, default=10.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="plan")


__all__ = ["MembershipPlan"]