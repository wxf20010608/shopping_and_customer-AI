from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/{user_id}",
    response_model=schemas.OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    user_id: int,
    payload: schemas.OrderCreate,
    db: Session = Depends(get_db),
):
    return order_service.create_order(user_id, payload, db)


@router.get("/{user_id}", response_model=List[schemas.OrderRead])
def list_orders(user_id: int, db: Session = Depends(get_db)):
    return order_service.list_orders(user_id, db)


@router.get("/detail/{order_id}", response_model=schemas.OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_order(order_id, db)


@router.delete("/{user_id}/{order_id}")
def delete_order(user_id: int, order_id: int, db: Session = Depends(get_db)):
    return order_service.delete_order(user_id, order_id, db)

