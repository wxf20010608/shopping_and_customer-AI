from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .timestamp_models import TimestampMixin

if TYPE_CHECKING:
    pass


class KnowledgeDocument(Base, TimestampMixin):
    """知识库文档模型"""
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")  # manual, pdf, web, api, database
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # 逗号分隔的标签
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 文档分块数量
    document_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)  # JSON 格式的元数据（来源、作者、时间、质量评分等）
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)  # 文档质量评分


class KnowledgeChunk(Base, TimestampMixin):
    """知识库文档块模型（用于向量化存储）"""
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 块在文档中的索引
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)  # JSON 格式的元数据
    vector_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)  # FAISS 向量索引 ID


__all__ = ["KnowledgeDocument", "KnowledgeChunk"]
