from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..models import User
from ..repositories import user_repository
from ..utils import hash_password, verify_password


def register_user(payload: schemas.UserCreate, db: Session) -> User:
    if user_repository.get_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if user_repository.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = user_repository.create_user(
        db,
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        address=payload.address,
    )
    user_repository.create_user_cart(db, user.id)
    db.commit()
    db.refresh(user)
    return user


def get_user(user_id: int, db: Session) -> User:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def login_user(payload: schemas.UserLogin, db: Session) -> User:
    identity = payload.identity
    # 先按用户名查找，不存在则按邮箱查找
    user = user_repository.get_by_username(db, identity) or user_repository.get_by_email(db, identity)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名/邮箱或密码错误")
    return user


def update_user(user_id: int, payload: schemas.UserUpdate, db: Session) -> User:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    data = payload.model_dump(exclude_unset=True)
    # 处理唯一性校验
    new_username = data.get("username")
    new_email = data.get("email")
    if new_username and new_username != user.username:
        if user_repository.get_by_username(db, new_username):
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = new_username
    if new_email and new_email != user.email:
        if user_repository.get_by_email(db, new_email):
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        user.email = new_email

    # 其他可更新字段
    for field in ("full_name", "phone", "address"):
        if field in data:
            setattr(user, field, data[field])

    db.commit()
    db.refresh(user)
    return user


def delete_user(user_id: int, db: Session) -> dict:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    from ..models import Cart, Order, Address, Membership, UserCoupon

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        for item in list(cart.items):
            db.delete(item)
        db.delete(cart)

    db.query(Address).filter(Address.user_id == user_id).delete()

    m = db.query(Membership).filter(Membership.user_id == user_id).first()
    if m:
        db.delete(m)

    db.query(UserCoupon).filter(UserCoupon.user_id == user_id).delete()

    orders = db.query(Order).filter(Order.user_id == user_id).all()
    for o in orders:
        db.delete(o)

    db.delete(user)
    db.commit()
    return {"deleted": True}

