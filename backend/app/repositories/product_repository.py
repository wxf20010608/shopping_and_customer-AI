from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Product


def create(db: Session, data: dict) -> Product:
    product = Product(**data)
    db.add(product)
    db.flush()
    return product


def list_products(db: Session, search: Optional[str]) -> List[Product]:
    query = db.query(Product)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(like_pattern)) | (Product.category.ilike(like_pattern))
        )
    return query.order_by(Product.created_at.desc()).all()


def get_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()

