from sqlalchemy.orm import Session

from ..models import Address


def list_addresses(db: Session, user_id: int):
    return db.query(Address).filter(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.id.desc()).all()


def get_by_id(db: Session, address_id: int):
    return db.query(Address).filter(Address.id == address_id).first()


def create_address(db: Session, user_id: int, **kwargs) -> Address:
    addr = Address(user_id=user_id, **kwargs)
    db.add(addr)
    db.flush()
    return addr


def update_address(db: Session, addr: Address, **kwargs) -> Address:
    for k, v in kwargs.items():
        setattr(addr, k, v)
    db.flush()
    return addr


def delete_address(db: Session, addr: Address):
    db.delete(addr)
    db.flush()


def unset_default(db: Session, user_id: int):
    db.query(Address).filter(Address.user_id == user_id, Address.is_default == True).update({Address.is_default: False})
    db.flush()