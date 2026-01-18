# backend/app/admin_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
import os, secrets

from .database import get_db
from . import schemas
from .models import Product, Order, OrderItem, CartItem, Cart, OrderStatusEnum, ShippingStatusEnum, ShippingInfo, User, Category, Coupon, UserCoupon, Membership, MembershipPlan, MembershipCard, ChatMessage

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    u = os.environ.get("ADMIN_USERNAME", "admin")
    p = os.environ.get("ADMIN_PASSWORD", "123456")
    if not (secrets.compare_digest(credentials.username, u) and secrets.compare_digest(credentials.password, p)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin authentication failed", headers={"WWW-Authenticate": "Basic"})
    return True

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/status")
def admin_status(_: bool = Depends(verify_admin)):
    return {"status": "ok"}

@admin_router.get("/users", response_model=list[schemas.UserRead])
def list_users(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.desc()).all()

@admin_router.get("/products", response_model=schemas.ProductPage)
def admin_list_products(_: bool = Depends(verify_admin), search: str | None = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    query = db.query(Product)
    if search:
        like = f"%{search}%"
        query = query.filter((Product.name.ilike(like)) | (Product.category.ilike(like)))
    total = query.count()
    items = query.order_by(Product.id.desc()).offset((max(page,1)-1)*max(page_size,1)).limit(max(page_size,1)).all()
    return schemas.ProductPage(items=items, total=total, page=max(page,1), page_size=max(page_size,1))

@admin_router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def admin_create_product(payload: schemas.ProductCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    p = Product(**payload.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@admin_router.put("/products/{product_id}", response_model=schemas.ProductRead)
def admin_update_product(product_id: int, payload: schemas.ProductUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    from .services import product_service
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p: raise HTTPException(status_code=404, detail="商品不存在")
    data = payload.model_dump(exclude_unset=True)
    
    # 如果更新了名称或分类，且没有手动提供图片URL，则根据新名称和商品ID自动生成图片
    name_changed = 'name' in data and data['name'] != p.name
    category_changed = 'category' in data and data['category'] != p.category
    image_provided = 'image_url' in data
    
    # 如果名称或分类改变，且没有手动提供图片，则自动生成（使用商品ID确保唯一性）
    if (name_changed or category_changed) and not image_provided:
        new_name = data.get('name', p.name)
        new_category = data.get('category', p.category)
        data['image_url'] = product_service._generate_image_url_from_name(new_name, new_category, p.id)
    
    for k,v in data.items(): setattr(p,k,v)
    db.commit(); db.refresh(p)
    return p

@admin_router.delete("/products/{product_id}")
def admin_delete_product(product_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p: raise HTTPException(status_code=404, detail="商品不存在")
    ref_order = db.query(OrderItem.id).filter(OrderItem.product_id == product_id).first()
    ref_cart = db.query(CartItem.id).filter(CartItem.product_id == product_id).first()
    if ref_order or ref_cart:
        raise HTTPException(status_code=400, detail="商品已被订单或购物车引用，禁止删除")
    db.delete(p); db.commit()
    return {"status":"ok"}

@admin_router.get("/orders", response_model=list[schemas.OrderRead])
def admin_list_orders(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return (db.query(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.shipping))
            .order_by(Order.id.desc()).all())

@admin_router.put("/orders/{order_id}/status", response_model=schemas.OrderRead)
def admin_update_order_status(order_id: int, status_value: OrderStatusEnum, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="订单不存在")
    order.status = status_value; db.commit(); db.refresh(order)
    return order

@admin_router.put("/logistics/{order_id}", response_model=schemas.ShippingInfoRead)
def admin_update_logistics(order_id: int, status_value: ShippingStatusEnum, tracking_number: str | None = None, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    shipping = db.query(ShippingInfo).filter(ShippingInfo.order_id == order_id).first()
    if not shipping: raise HTTPException(status_code=404, detail="物流信息不存在")
    if tracking_number: shipping.tracking_number = tracking_number
    shipping.status = status_value
    db.commit(); db.refresh(shipping)
    return shipping

@admin_router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def admin_create_user(payload: schemas.UserCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    from .utils import hash_password
    user_data = payload.model_dump()
    user_data["password_hash"] = hash_password(user_data.pop("password"))
    user = User(**user_data)
    db.add(user); db.commit(); db.refresh(user)
    return user

@admin_router.put("/users/{user_id}", response_model=schemas.UserRead)
def admin_update_user(user_id: int, payload: schemas.UserUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="用户不存在")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        from .utils import hash_password
        data["password_hash"] = hash_password(data.pop("password"))
    for k,v in data.items(): setattr(user,k,v)
    db.commit(); db.refresh(user)
    return user

@admin_router.get("/categories", response_model=list[schemas.CategoryRead])
def admin_list_categories(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id.desc()).all()

@admin_router.post("/categories", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
def admin_create_category(payload: schemas.CategoryCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    category = Category(**payload.model_dump())
    db.add(category); db.commit(); db.refresh(category)
    return category

@admin_router.put("/categories/{category_id}", response_model=schemas.CategoryRead)
def admin_update_category(category_id: int, payload: schemas.CategoryUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category: raise HTTPException(status_code=404, detail="分类不存在")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(category,k,v)
    db.commit(); db.refresh(category)
    return category

@admin_router.delete("/categories/{category_id}")
def admin_delete_category(category_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category: raise HTTPException(status_code=404, detail="分类不存在")
    ref_products = db.query(Product.id).filter(Product.category_id == category_id).first()
    if ref_products:
        raise HTTPException(status_code=400, detail="分类下有商品，禁止删除")
    db.delete(category); db.commit()
    return {"status":"ok"}

@admin_router.post("/products/bulk", response_model=list[schemas.ProductRead], status_code=status.HTTP_201_CREATED)
def admin_bulk_create_products(payload: list[schemas.ProductCreate], _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    products = [Product(**p.model_dump()) for p in payload]
    db.add_all(products); db.commit()
    for p in products: db.refresh(p)
    return products

@admin_router.get("/stats")
def admin_stats(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    products_count = db.query(Product).count()
    orders_count = db.query(Order).count()
    orders_by_status = {s.value: db.query(Order).filter(Order.status == s).count() for s in OrderStatusEnum}
    sales_rows = (
        db.query(func.date(Order.created_at), func.sum(Order.total_amount))
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at).desc())
        .limit(7)
        .all()
    )
    top_cat_rows = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .limit(10)
        .all()
    )
    return {
        "users_count": users_count,
        "products_count": products_count,
        "orders_count": orders_count,
        "orders_by_status": orders_by_status,
        "sales_by_day": [{"date": r[0], "amount": float(r[1] or 0)} for r in sales_rows],
        "top_categories": [{"category": r[0] or "未分类", "count": int(r[1] or 0)} for r in top_cat_rows],
    }

@admin_router.get("/chats", response_model=list[schemas.ChatMessageRead])
def admin_list_chats(
    _: bool = Depends(verify_admin),
    user_id: int | None = None,
    product_id: int | None = None,
    role: str | None = None,
    q: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取聊天记录列表（支持筛选和数量限制，避免一次性加载过多数据导致卡顿）
    
    参数:
    - user_id: 筛选特定用户的聊天记录
    - product_id: 筛选特定商品的聊天记录
    - role: 筛选角色 (user/assistant)
    - q: 搜索关键词（搜索消息内容）
    - limit: 最大返回数量（默认100，最大500，避免系统卡顿）
    """
    query = db.query(ChatMessage)
    
    # 筛选条件
    if user_id is not None:
        query = query.filter(ChatMessage.user_id == user_id)
    if product_id is not None:
        query = query.filter(ChatMessage.product_id == product_id)
    if role:
        query = query.filter(ChatMessage.role == role)
    if q:
        like = f"%{q}%"
        query = query.filter(ChatMessage.content.ilike(like))
    
    # 限制返回数量，避免一次性加载过多数据导致系统卡顿
    # 默认100条，最大500条
    actual_limit = max(1, min(limit or 100, 500))
    
    # 执行查询并限制数量
    items = query.order_by(ChatMessage.id.desc()).limit(actual_limit).all()
    return items

@admin_router.delete("/chats/{chat_id}")
def admin_delete_chat(chat_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    chat = db.query(ChatMessage).filter(ChatMessage.id == chat_id).first()
    if not chat: raise HTTPException(status_code=404, detail="聊天记录不存在")
    db.delete(chat); db.commit()
    return {"status":"ok"}

@admin_router.delete("/chats/conversation")
def admin_delete_conversation(user_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
    return {"status":"ok"}

@admin_router.get("/coupons", response_model=list[schemas.CouponRead])
def admin_list_coupons(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(Coupon).order_by(Coupon.id.desc()).all()

@admin_router.post("/coupons", response_model=schemas.CouponRead, status_code=status.HTTP_201_CREATED)
def admin_create_coupon(payload: schemas.CouponCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    coupon = Coupon(**payload.model_dump())
    db.add(coupon); db.commit(); db.refresh(coupon)
    return coupon

@admin_router.put("/coupons/{coupon_id}", response_model=schemas.CouponRead)
def admin_update_coupon(coupon_id: int, payload: schemas.CouponUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon: raise HTTPException(status_code=404, detail="优惠券不存在")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(coupon,k,v)
    db.commit(); db.refresh(coupon)
    return coupon

@admin_router.delete("/coupons/{coupon_id}")
def admin_delete_coupon(coupon_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon: raise HTTPException(status_code=404, detail="优惠券不存在")
    db.delete(coupon); db.commit()
    return {"status":"ok"}

@admin_router.post("/coupons/{coupon_id}/assign/{user_id}", response_model=schemas.UserCouponRead)
def admin_assign_coupon(coupon_id: int, user_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    user_coupon = UserCoupon(user_id=user_id, coupon_id=coupon_id)
    db.add(user_coupon); db.commit(); db.refresh(user_coupon)
    return user_coupon

@admin_router.post("/coupons/{coupon_id}/assign/bulk")
def admin_assign_coupon_bulk(coupon_id: int, payload: dict, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    user_ids = payload.get("user_ids", [])
    for user_id in user_ids:
        user_coupon = UserCoupon(user_id=user_id, coupon_id=coupon_id)
        db.add(user_coupon)
    db.commit()
    return {"status":"ok", "assigned_count": len(user_ids)}

@admin_router.get("/coupons/auto-issue/rules")
def admin_get_auto_issue_rules(_: bool = Depends(verify_admin)):
    """获取优惠券自动发放规则配置"""
    try:
        from ..services.coupon_auto_issue_service import get_auto_issue_service
        auto_issue_service = get_auto_issue_service()
        return {
            "enabled": auto_issue_service.enabled,
            "rules": auto_issue_service.rules,
            "config": {
                "COUPON_AUTO_ISSUE_ENABLED": auto_issue_service.enabled,
                "COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID": os.environ.get("COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID"),
                "COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID": os.environ.get("COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID"),
            }
        }
    except Exception as e:
        return {"enabled": False, "error": str(e)}

@admin_router.post("/coupons/auto-issue/config")
def admin_set_auto_issue_config(payload: dict, _: bool = Depends(verify_admin)):
    """配置优惠券自动发放规则"""
    try:
        import os
        if "COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID" in payload:
            os.environ["COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID"] = str(payload["COUPON_AUTO_ISSUE_NEW_USER_COUPON_ID"])
        if "COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID" in payload:
            os.environ["COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID"] = str(payload["COUPON_AUTO_ISSUE_FIRST_ORDER_COUPON_ID"])
        return {"status": "ok", "message": "配置已更新"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"配置更新失败: {str(e)}")

@admin_router.get("/memberships", response_model=list[schemas.MembershipRead])
def admin_list_memberships(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(Membership).order_by(Membership.id.desc()).all()

@admin_router.post("/memberships/{user_id}", response_model=schemas.MembershipRead, status_code=status.HTTP_201_CREATED)
def admin_create_membership(user_id: int, payload: schemas.MembershipCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    membership = Membership(user_id=user_id, **payload.model_dump())
    db.add(membership); db.commit(); db.refresh(membership)
    return membership

@admin_router.put("/memberships/{user_id}", response_model=schemas.MembershipRead)
def admin_update_membership(user_id: int, payload: schemas.MembershipUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    membership = db.query(Membership).filter(Membership.user_id == user_id).first()
    if not membership: raise HTTPException(status_code=404, detail="会员信息不存在")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(membership,k,v)
    db.commit(); db.refresh(membership)
    return membership

@admin_router.delete("/memberships/{user_id}")
def admin_delete_membership(user_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    membership = db.query(Membership).filter(Membership.user_id == user_id).first()
    if not membership: raise HTTPException(status_code=404, detail="会员信息不存在")
    db.delete(membership); db.commit()
    return {"status":"ok"}

@admin_router.get("/membership-plans", response_model=list[schemas.MembershipPlanRead])
def admin_list_membership_plans(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(MembershipPlan).order_by(MembershipPlan.id.desc()).all()

@admin_router.post("/membership-plans", response_model=schemas.MembershipPlanRead, status_code=status.HTTP_201_CREATED)
def admin_create_membership_plan(payload: schemas.MembershipPlanCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    plan = MembershipPlan(**payload.model_dump())
    db.add(plan); db.commit(); db.refresh(plan)
    return plan

@admin_router.put("/membership-plans/{plan_id}", response_model=schemas.MembershipPlanRead)
def admin_update_membership_plan(plan_id: int, payload: schemas.MembershipPlanUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not plan: raise HTTPException(status_code=404, detail="会员计划不存在")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(plan,k,v)
    db.commit(); db.refresh(plan)
    return plan

@admin_router.delete("/membership-plans/{plan_id}")
def admin_delete_membership_plan(plan_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not plan: raise HTTPException(status_code=404, detail="会员计划不存在")
    db.delete(plan); db.commit()
    return {"status":"ok"}

@admin_router.get("/membership-cards", response_model=list[schemas.MembershipCardRead])
def admin_list_membership_cards(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    return db.query(MembershipCard).order_by(MembershipCard.id.desc()).all()

@admin_router.post("/membership-cards", response_model=schemas.MembershipCardRead, status_code=status.HTTP_201_CREATED)
def admin_create_membership_card(payload: schemas.MembershipCardCreate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    card = MembershipCard(**payload.model_dump())
    db.add(card); db.commit(); db.refresh(card)
    return card

@admin_router.put("/membership-cards/{card_id}", response_model=schemas.MembershipCardRead)
def admin_update_membership_card(card_id: int, payload: schemas.MembershipCardUpdate, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    card = db.query(MembershipCard).filter(MembershipCard.id == card_id).first()
    if not card: raise HTTPException(status_code=404, detail="会员卡不存在")
    data = payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(card,k,v)
    db.commit(); db.refresh(card)
    return card

@admin_router.delete("/membership-cards/{card_id}")
def admin_delete_membership_card(card_id: int, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    card = db.query(MembershipCard).filter(MembershipCard.id == card_id).first()
    if not card: raise HTTPException(status_code=404, detail="会员卡不存在")
    db.delete(card); db.commit()
    return {"status":"ok"}

@admin_router.post("/products/{product_id}/image", response_model=schemas.ProductRead)
def admin_upload_product_image(product_id: int, file: UploadFile = File(...), request: Request = None, _: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product: raise HTTPException(status_code=404, detail="商品不存在")
    
    from pathlib import Path
    import time
    
    BASE_DIR = Path(__file__).resolve().parent
    STATIC_DIR = BASE_DIR / "static"
    UPLOAD_DIR = STATIC_DIR / "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ext = Path(file.filename or "").suffix or ".bin"
    name = f"product_{int(time.time())}_{os.urandom(4).hex()}{ext}"
    dest = UPLOAD_DIR / name
    
    with open(dest, "wb") as fp:
        fp.write(file.file.read())
    
    product.image_url = f"/static/uploads/{name}"
    db.commit(); db.refresh(product)
    return product