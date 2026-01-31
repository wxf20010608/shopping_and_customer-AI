from sqlalchemy.orm import Session, selectinload

from ..models import Cart, CartItem, User


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    hashed_password: str,
    full_name: str | None,
    phone: str | None,
    address: str | None,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        phone=phone,
        address=address,
    )
    db.add(user)
    db.flush()
    return user


def create_user_cart(db: Session, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.flush()
    return cart


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_with_cart(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(
            selectinload(User.cart)
            .selectinload(Cart.items)
            .selectinload(CartItem.product)
        )
        .filter(User.id == user_id)
        .first()
    )

