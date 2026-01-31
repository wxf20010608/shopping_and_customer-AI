from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from .. import schemas
from ..models import Cart, CartItem, Product, User


def _ensure_cart(db: Session, user_id: int) -> Cart:
    cart = (
        db.query(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .filter(Cart.user_id == user_id)
        .first()
    )
    if cart:
        return cart

    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="用户不存在")

    cart = Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart(db: Session, user_id: int) -> Cart:
    return _ensure_cart(db, user_id)


def add_item(
    db: Session,
    user_id: int,
    payload: schemas.CartItemCreate,
) -> Cart:
    cart = _ensure_cart(db, user_id)
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="库存不足")

    item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == payload.product_id)
        .first()
    )
    if item:
        if product.stock < payload.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        item.quantity += payload.quantity
        product.stock -= payload.quantity
    else:
        if product.stock < payload.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        item = CartItem(
            cart_id=cart.id, product_id=payload.product_id, quantity=payload.quantity
        )
        db.add(item)
        product.stock -= payload.quantity

    db.commit()
    return _ensure_cart(db, user_id)


def update_item(
    db: Session,
    user_id: int,
    item_id: int,
    payload: schemas.CartItemCreate,
) -> Cart:
    cart = _ensure_cart(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")

    old_product = db.query(Product).filter(Product.id == item.product_id).first()
    new_product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not new_product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if payload.product_id != item.product_id:
        if new_product.stock < payload.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        if old_product:
            old_product.stock += item.quantity
        new_product.stock -= payload.quantity
        item.product_id = payload.product_id
        item.quantity = payload.quantity
    else:
        delta = payload.quantity - item.quantity
        if delta > 0:
            if new_product.stock < delta:
                raise HTTPException(status_code=400, detail="库存不足")
            new_product.stock -= delta
        elif delta < 0:
            new_product.stock += (-delta)
        item.quantity = payload.quantity

    db.commit()
    return _ensure_cart(db, user_id)


def remove_item(db: Session, user_id: int, item_id: int) -> Cart:
    cart = _ensure_cart(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product:
        product.stock += item.quantity
    db.delete(item)
    db.commit()
    return _ensure_cart(db, user_id)


def clear_items(db: Session, user_id: int) -> Cart:
    cart = _ensure_cart(db, user_id)
    for item in list(cart.items):
        p = db.query(Product).filter(Product.id == item.product_id).first()
        if p:
            p.stock += item.quantity
        db.delete(item)
    db.commit()
    return _ensure_cart(db, user_id)

