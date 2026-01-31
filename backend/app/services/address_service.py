from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..repositories import address_repository, user_repository


def ensure_user(db: Session, user_id: int):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def list_addresses(user_id: int, db: Session):
    ensure_user(db, user_id)
    return address_repository.list_addresses(db, user_id)


def create_address(user_id: int, payload: schemas.AddressCreate, db: Session):
    ensure_user(db, user_id)
    if payload.is_default:
        address_repository.unset_default(db, user_id)
    addr = address_repository.create_address(
        db,
        user_id=user_id,
        receiver_name=payload.receiver_name,
        phone=payload.phone,
        province=payload.province,
        city=payload.city,
        district=payload.district,
        detail=payload.detail,
        is_default=payload.is_default,
    )
    db.commit()
    db.refresh(addr)
    return addr


def update_address(user_id: int, address_id: int, payload: schemas.AddressUpdate, db: Session):
    ensure_user(db, user_id)
    addr = address_repository.get_by_id(db, address_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="地址不存在")
    update_fields = payload.model_dump(exclude_unset=True)
    if update_fields.get("is_default"):
        address_repository.unset_default(db, user_id)
    addr = address_repository.update_address(db, addr, **update_fields)
    db.commit()
    db.refresh(addr)
    return addr


def delete_address(user_id: int, address_id: int, db: Session):
    ensure_user(db, user_id)
    addr = address_repository.get_by_id(db, address_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="地址不存在")
    address_repository.delete_address(db, addr)
    db.commit()
    return {"status": "ok"}