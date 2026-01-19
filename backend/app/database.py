from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pathlib import Path

DATABASE_URL = f"sqlite:///{(Path(__file__).resolve().parent.parent / 'smart_mall.db').as_posix()}"


class Base(DeclarativeBase):
    """SQLAlchemy 基礎模型。"""


engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator:
    """獲取資料庫會話，用於 FastAPI 依賴注入。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator:
    """上下文管理器，方便在腳本或背景任務中使用資料庫會話。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

