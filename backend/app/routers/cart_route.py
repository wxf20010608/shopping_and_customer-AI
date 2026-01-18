from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import cart_service

router = APIRouter(prefix="/carts", tags=["carts"])


@router.get("/{user_id}", response_model=schemas.CartRead)
def get_cart(user_id: int, db: Session = Depends(get_db)):
    return cart_service.get_cart(db, user_id)


@router.post(
    "/{user_id}/items",
    response_model=schemas.CartRead,
    status_code=status.HTTP_201_CREATED,
)
def add_item_to_cart(
    user_id: int, payload: schemas.CartItemCreate, db: Session = Depends(get_db)
):
    return cart_service.add_item(db, user_id, payload)


@router.put(
    "/{user_id}/items/{item_id}",
    response_model=schemas.CartRead,
)
def update_cart_item(
    user_id: int, item_id: int, payload: schemas.CartItemCreate, db: Session = Depends(get_db)
):
    return cart_service.update_item(db, user_id, item_id, payload)


@router.delete(
    "/{user_id}/items/{item_id}",
    response_model=schemas.CartRead,
)
def remove_cart_item(user_id: int, item_id: int, db: Session = Depends(get_db)):
    return cart_service.remove_item(db, user_id, item_id)


@router.delete(
    "/{user_id}/items",
    response_model=schemas.CartRead,
)
def clear_cart(user_id: int, db: Session = Depends(get_db)):
    return cart_service.clear_items(db, user_id)

