from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Membership, User, MembershipPlan
from .. import schemas


def get_or_404(db: Session, user_id: int) -> Membership:
    m = db.query(Membership).filter(Membership.user_id == user_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="会员不存在")
    return m


def get(db: Session, user_id: int) -> Membership | None:
    return db.query(Membership).filter(Membership.user_id == user_id).first()


def create(user_id: int, payload: schemas.MembershipCreate, db: Session) -> Membership:
    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="用户不存在")
    if db.query(Membership.id).filter(Membership.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="该用户已开通会员")
    plan_id = payload.plan_id
    if plan_id:
        plan = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id, MembershipPlan.active == True).first()
        if not plan:
            raise HTTPException(status_code=400, detail="会员计划不可用")
    m = Membership(user_id=user_id, level=payload.level or "standard", plan_id=plan_id, extra_info=payload.extra_info)
    db.add(m); db.commit(); db.refresh(m)
    return m


def update(user_id: int, payload: schemas.MembershipUpdate, db: Session) -> Membership:
    m = get_or_404(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    if "plan_id" in data and data["plan_id"]:
        plan = db.query(MembershipPlan).filter(MembershipPlan.id == data["plan_id"], MembershipPlan.active == True).first()
        if not plan:
            raise HTTPException(status_code=400, detail="会员计划不可用")
    for k, v in data.items(): setattr(m, k, v)
    db.commit(); db.refresh(m)
    return m


def recharge(user_id: int, amount: float, db: Session) -> Membership:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    m = get_or_404(db, user_id)
    m.balance = (m.balance or 0) + amount
    db.commit(); db.refresh(m)
    return m