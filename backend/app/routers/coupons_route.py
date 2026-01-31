from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import coupon_service

router = APIRouter(prefix="/coupons", tags=["coupons"]) 


@router.get("/{user_id}", response_model=list[schemas.UserCouponRead])
def list_user_coupons(user_id: int, db: Session = Depends(get_db)):
    return coupon_service.list_user_coupons(user_id, db)