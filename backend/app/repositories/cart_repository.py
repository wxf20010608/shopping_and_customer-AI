from sqlalchemy.orm import Session, selectinload

from ..models import Cart, CartItem


def get_by_user_id(db: Session, user_id: int, with_items: bool = False) -> Cart | None:
    query = db.query(Cart).filter(Cart.user_id == user_id)
    if with_items:
        query = query.options(selectinload(Cart.items).selectinload(CartItem.product))
    return query.first()


def create_cart(db: Session, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.flush()
    return cart


def get_item(db: Session, cart_id: int, product_id: int) -> CartItem | None:
    return (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        .first()
    )


def create_item(db: Session, *, cart_id: int, product_id: int, quantity: int) -> CartItem:
    item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.flush()
    return item


def delete_item(db: Session, item: CartItem) -> None:
    db.delete(item)


def clear_items(db: Session, cart: Cart) -> None:
    for item in list(cart.items):
        db.delete(item)

