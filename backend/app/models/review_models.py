"""
商品评价和评分模型
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, Float, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    from .product_models import Product
    from .user_models import User
    from .order_models import Order


class Review(Base, TimestampMixin):
    """商品评价模型"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 评分 1-5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)  # 评价内容
    images: Mapped[str | None] = mapped_column(Text, nullable=True)  # 图片URLs（JSON数组字符串）
    
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)  # 有用数
    verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否购买验证
    status: Mapped[str] = mapped_column(String(20), default="approved")  # 状态：pending, approved, rejected
    
    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")
    order: Mapped["Order"] = relationship(back_populates="reviews")


__all__ = ["Review"]
