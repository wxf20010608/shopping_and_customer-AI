# backend/app/admin_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
import os, secrets

<<<<<<< HEAD
from app.database import get_db
from app import schemas
from app.models import Product, Order, OrderItem, CartItem, Cart, OrderStatusEnum, ShippingStatusEnum, ShippingInfo, User, Category, Coupon, UserCoupon, Membership, MembershipPlan, MembershipCard, ChatMessage, Review
from app.services.statistics_service import get_statistics_service
from app.services.stock_alert_service import get_stock_alert_service
from app.services.cache_service import get_cache_service
from app.services import review_service
=======
from .database import get_db
from . import schemas
from .models import Product, Order, OrderItem, CartItem, Cart, OrderStatusEnum, ShippingStatusEnum, ShippingInfo, User, Category, Coupon, UserCoupon, Membership, MembershipPlan, MembershipCard, ChatMessage, Review
from .services.statistics_service import get_statistics_service
from .services.stock_alert_service import get_stock_alert_service
from .services.cache_service import get_cache_service
from .services import review_service
>>>>>>> small_shopping_version1.0.0

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
<<<<<<< HEAD
    from app.services import product_service
=======
    from .services import product_service
>>>>>>> small_shopping_version1.0.0
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
<<<<<<< HEAD
    from app.utils import hash_password
=======
    from .utils import hash_password
>>>>>>> small_shopping_version1.0.0
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
<<<<<<< HEAD
        from app.utils import hash_password
=======
        from .utils import hash_password
>>>>>>> small_shopping_version1.0.0
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
<<<<<<< HEAD
        from app.services.coupon_auto_issue_service import get_auto_issue_service
=======
        from .services.coupon_auto_issue_service import get_auto_issue_service
>>>>>>> small_shopping_version1.0.0
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

@admin_router.post("/coupons/auto-issue/rules")
def admin_create_auto_issue_rule(payload: dict, _: bool = Depends(verify_admin)):
    """创建优惠券自动发放规则"""
    try:
<<<<<<< HEAD
        from app.services.coupon_auto_issue_service import get_auto_issue_service
=======
        from .services.coupon_auto_issue_service import get_auto_issue_service
>>>>>>> small_shopping_version1.0.0
        auto_issue_service = get_auto_issue_service()
        rule_id = payload.get("rule_id") or f"rule_{len(auto_issue_service.rules) + 1}"
        rule = {
            "trigger": payload.get("trigger"),  # 'register', 'first_order', 'birthday', 'cron', 'date'
            "coupon_id": payload.get("coupon_id"),
            "condition": payload.get("condition"),
            "cron": payload.get("cron"),
            "enabled": payload.get("enabled", True),
            "scheduled_date": payload.get("scheduled_date"),  # 指定日期触发器的日期时间
            "birthday_hour": payload.get("birthday_hour", 9),  # 生日触发器的发送时间（小时）
            "delay_seconds": payload.get("delay_seconds", 0)   # 注册/首购触发器的延迟秒数
        }
        auto_issue_service.register_rule(rule_id, rule)
        return {"status": "ok", "message": "规则已创建", "rule_id": rule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建规则失败: {str(e)}")

@admin_router.put("/coupons/auto-issue/rules/{rule_id}")
def admin_update_auto_issue_rule(rule_id: str, payload: dict, _: bool = Depends(verify_admin)):
    """更新优惠券自动发放规则"""
    try:
<<<<<<< HEAD
        from app.services.coupon_auto_issue_service import get_auto_issue_service
=======
        from .services.coupon_auto_issue_service import get_auto_issue_service
>>>>>>> small_shopping_version1.0.0
        auto_issue_service = get_auto_issue_service()
        if rule_id not in auto_issue_service.rules:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 更新规则
        existing_rule = auto_issue_service.rules[rule_id]
        if "trigger" in payload:
            existing_rule["trigger"] = payload["trigger"]
        if "coupon_id" in payload:
            existing_rule["coupon_id"] = payload["coupon_id"]
        if "condition" in payload:
            existing_rule["condition"] = payload["condition"]
        if "cron" in payload:
            existing_rule["cron"] = payload["cron"]
        if "enabled" in payload:
            existing_rule["enabled"] = payload["enabled"]
        if "scheduled_date" in payload:
            existing_rule["scheduled_date"] = payload["scheduled_date"]
        if "birthday_hour" in payload:
            existing_rule["birthday_hour"] = payload["birthday_hour"]
        if "delay_seconds" in payload:
            existing_rule["delay_seconds"] = payload["delay_seconds"]
        
        return {"status": "ok", "message": "规则已更新"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新规则失败: {str(e)}")

@admin_router.delete("/coupons/auto-issue/rules/{rule_id}")
def admin_delete_auto_issue_rule(rule_id: str, _: bool = Depends(verify_admin)):
    """删除优惠券自动发放规则"""
    try:
<<<<<<< HEAD
        from app.services.coupon_auto_issue_service import get_auto_issue_service
=======
        from .services.coupon_auto_issue_service import get_auto_issue_service
>>>>>>> small_shopping_version1.0.0
        auto_issue_service = get_auto_issue_service()
        if rule_id not in auto_issue_service.rules:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        del auto_issue_service.rules[rule_id]
        return {"status": "ok", "message": "规则已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除规则失败: {str(e)}")

# Redis 缓存管理接口
@admin_router.get("/cache/status")
def admin_get_cache_status(_: bool = Depends(verify_admin)):
    """获取缓存状态"""
    try:
        cache_service = get_cache_service()
        
        # 获取缓存统计信息
        stats = {
            "enabled": cache_service.enabled,
            "connected": cache_service.redis_client is not None,
            "keys_count": 0
        }
        
        if cache_service.enabled and cache_service.redis_client:
            try:
                # 统计所有键的数量
                keys = cache_service.redis_client.keys("*")
                stats["keys_count"] = len(keys) if keys else 0
                
                # 获取内存使用情况（如果支持）
                try:
                    info = cache_service.redis_client.info("memory")
                    stats["memory_used"] = info.get("used_memory_human", "N/A")
                except:
                    pass
            except Exception as e:
                stats["error"] = str(e)
        
        return stats
    except Exception as e:
        return {"enabled": False, "connected": False, "error": str(e)}

@admin_router.post("/cache/clear")
def admin_clear_cache(_: bool = Depends(verify_admin)):
    """清空所有缓存"""
    try:
        cache_service = get_cache_service()
        
        if not cache_service.enabled or not cache_service.redis_client:
            return {"status": "error", "message": "缓存服务未启用"}
        
        success = cache_service.clear()
        if success:
            return {"status": "ok", "message": "缓存已清空"}
        else:
            return {"status": "error", "message": "清空缓存失败"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

@admin_router.delete("/cache/{pattern}")
def admin_delete_cache_pattern(pattern: str, _: bool = Depends(verify_admin)):
    """按模式删除缓存"""
    try:
        cache_service = get_cache_service()
        
        if not cache_service.enabled or not cache_service.redis_client:
            return {"status": "error", "message": "缓存服务未启用"}
        
        count = cache_service.delete_pattern(pattern)
        return {"status": "ok", "message": f"已删除 {count} 个缓存键", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除缓存失败: {str(e)}")

# 日志查看接口
@admin_router.get("/logs/files")
def admin_list_log_files(_: bool = Depends(verify_admin)):
    """获取日志文件列表"""
    try:
<<<<<<< HEAD
        from app.services.log_service import get_log_service
=======
        from .services.log_service import get_log_service
>>>>>>> small_shopping_version1.0.0
        log_service = get_log_service()
        return log_service.list_log_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志文件列表失败: {str(e)}")

@admin_router.get("/logs/stats")
def admin_get_log_stats(_: bool = Depends(verify_admin)):
    """获取日志统计信息"""
    try:
<<<<<<< HEAD
        from app.services.log_service import get_log_service
=======
        from .services.log_service import get_log_service
>>>>>>> small_shopping_version1.0.0
        log_service = get_log_service()
        return log_service.get_log_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")

@admin_router.get("/logs/read/{filename}")
def admin_read_log_file(
    filename: str,
    lines: int = Query(1000, ge=1, le=10000, description="读取行数"),
    level: str = Query(None, description="日志级别过滤（DEBUG/INFO/WARNING/ERROR/CRITICAL）"),
    search: str = Query(None, description="搜索文本"),
    reverse: bool = Query(True, description="是否反向读取（从文件末尾开始）"),
    _: bool = Depends(verify_admin)
):
    """读取日志文件内容"""
    try:
<<<<<<< HEAD
        from app.services.log_service import get_log_service
=======
        from .services.log_service import get_log_service
>>>>>>> small_shopping_version1.0.0
        log_service = get_log_service()
        return log_service.read_log_file(
            filename=filename,
            lines=lines,
            level_filter=level,
            search_text=search,
            reverse=reverse
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取日志文件失败: {str(e)}")

@admin_router.delete("/logs/clear/{filename}")
def admin_clear_log_file(filename: str, _: bool = Depends(verify_admin)):
    """清空日志文件"""
    try:
<<<<<<< HEAD
        from app.services.log_service import get_log_service
=======
        from .services.log_service import get_log_service
>>>>>>> small_shopping_version1.0.0
        log_service = get_log_service()
        return log_service.clear_log_file(filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空日志文件失败: {str(e)}")

# 数据统计接口
@admin_router.get("/statistics/dashboard")
def admin_get_dashboard_stats(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    """获取仪表板统计数据"""
    try:
        stats_service = get_statistics_service()
        return stats_service.get_dashboard_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@admin_router.get("/statistics/sales")
def admin_get_sales_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取销售统计（按日期）"""
    try:
        stats_service = get_statistics_service()
        return stats_service.get_sales_statistics(db, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取销售统计失败: {str(e)}")

@admin_router.get("/statistics/products")
def admin_get_product_statistics(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    """获取商品销售统计"""
    try:
        stats_service = get_statistics_service()
        return stats_service.get_product_statistics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品统计失败: {str(e)}")

@admin_router.get("/statistics/users")
def admin_get_user_statistics(_: bool = Depends(verify_admin), db: Session = Depends(get_db)):
    """获取用户统计"""
    try:
        stats_service = get_statistics_service()
        return stats_service.get_user_statistics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")

# 库存预警接口
@admin_router.get("/stock-alerts")
def admin_get_stock_alerts(
    threshold: int = Query(10, ge=0, description="预警阈值"),
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取库存预警列表"""
    try:
        alert_service = get_stock_alert_service()
        return {"alerts": alert_service.check_low_stock_products(db, threshold)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取库存预警失败: {str(e)}")

@admin_router.get("/stock-alerts/statistics")
def admin_get_stock_statistics(
    threshold: int = Query(None, ge=0, description="预警阈值（可选，不传则使用默认值）"),
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取库存统计"""
    try:
        alert_service = get_stock_alert_service()
        return alert_service.get_stock_statistics(db, threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取库存统计失败: {str(e)}")

# 评价管理接口
@admin_router.get("/reviews")
def admin_list_reviews(
    product_id: int | None = Query(None, description="商品ID筛选"),
    status: str | None = Query(None, description="评价状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取评价列表（管理员）"""
    try:
        # 处理空值：如果 product_id 是 0 或空字符串，转为 None
        if product_id is not None and product_id <= 0:
            product_id = None
        
        # 处理空值：如果 status 是空字符串，转为 None
        if status is not None and not status.strip():
            status = None
        
        result = review_service.list_reviews(
            product_id=product_id,
            user_id=None,  # 管理员查看所有用户的评价
            status=status,
            page=page,
            page_size=page_size,
            db=db
        )
        
        # 确保返回格式正确
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取评价列表失败: {str(e)}")

@admin_router.delete("/reviews/{review_id}")
def admin_delete_review(
    review_id: int,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """删除评价（管理员权限）"""
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="评价不存在")
        
        product_id = review.product_id
        db.delete(review)
        db.commit()
        
        # 更新商品平均评分（重新计算该商品的平均评分）
        from sqlalchemy import func
        result = db.query(func.avg(Review.rating)).filter(
            Review.product_id == product_id,
            Review.status == "approved"
        ).scalar()
        
        # 这里可以更新商品表的 average_rating 字段（如果存在）
        # 当前方案是在查询时动态计算
        
        return {"status": "ok", "message": "评价已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评价失败: {str(e)}")

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