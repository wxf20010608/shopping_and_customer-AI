from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import membership_service
from ..models.membership_plan_models import MembershipPlan
from ..models.membership_card_models import MembershipCard

router = APIRouter(prefix="/memberships", tags=["memberships"]) 


@router.get("/{user_id}", response_model=schemas.MembershipRead)
def get_membership(user_id: int, db: Session = Depends(get_db)):
    m = membership_service.get(db, user_id)
    if not m:
        # 兼容前端：返回404由前端决定是否创建
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="会员不存在")
    return m


@router.post("/{user_id}", response_model=schemas.MembershipRead, status_code=status.HTTP_201_CREATED)
def create_membership(user_id: int, payload: schemas.MembershipCreate, db: Session = Depends(get_db)):
    return membership_service.create(user_id, payload, db)


@router.put("/{user_id}", response_model=schemas.MembershipRead)
def update_membership(user_id: int, payload: schemas.MembershipUpdate, db: Session = Depends(get_db)):
    return membership_service.update(user_id, payload, db)


@router.post("/{user_id}/recharge", response_model=schemas.MembershipRead)
def recharge_membership(user_id: int, payload: schemas.MembershipRecharge, db: Session = Depends(get_db)):
    return membership_service.recharge(user_id, payload.amount, db)


@router.get("/plans", response_model=list[schemas.MembershipPlanRead])
def list_plans(db: Session = Depends(get_db)):
    return db.query(MembershipPlan).filter(MembershipPlan.active == True).order_by(MembershipPlan.id.asc()).all()


@router.get("/cards/published", response_model=list[schemas.MembershipCardRead])
def list_published_cards(db: Session = Depends(get_db)):
    return (
        db.query(MembershipCard)
        .filter(MembershipCard.published == True)
        .order_by(MembershipCard.id.desc())
        .all()
    )


@router.get("/{user_id}/cards", response_model=list[schemas.MembershipCardRead])
def list_user_cards(user_id: int, db: Session = Depends(get_db)):
    return db.query(MembershipCard).filter(MembershipCard.user_id == user_id).order_by(MembershipCard.id.desc()).all()