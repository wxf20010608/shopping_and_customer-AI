from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..models import ShippingStatusEnum
from ..services import logistics_service

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.get("/{order_id}", response_model=schemas.ShippingInfoRead)
def get_shipping_info(order_id: int, db: Session = Depends(get_db)):
    return logistics_service.get_shipping_info(order_id, db)


@router.put(
    "/{order_id}",
    response_model=schemas.ShippingInfoRead,
)
def update_shipping_status(
    order_id: int,
    status_value: ShippingStatusEnum,
    tracking_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return logistics_service.update_shipping_status(
        order_id=order_id,
        status_value=status_value,
        db=db,
        tracking_number=tracking_number,
    )

