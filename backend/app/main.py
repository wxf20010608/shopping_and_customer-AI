from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .utils import load_env
from .routers import (
    cart_route,
    logistics_route,
    orders_route,
    products_route,
    users_route,
)
from .routers import addresses_route, memberships_route, coupons_route, customer_service_route
from .routers import knowledge_base_route
from .admin_router import admin_router


def create_app() -> FastAPI:
    load_env()
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    from sqlalchemy import create_engine as _ce
    e = engine
    with e.connect() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(memberships)").fetchall()
        names = {r[1] for r in rows}
        if "plan_id" not in names:
            conn.exec_driver_sql("ALTER TABLE memberships ADD COLUMN plan_id INTEGER")
        mccols = {r[1] for r in conn.exec_driver_sql("PRAGMA table_info(membership_cards)").fetchall()}
        if "published" not in mccols:
            conn.exec_driver_sql("ALTER TABLE membership_cards ADD COLUMN published BOOLEAN DEFAULT 1")
        ocols = {r[1] for r in conn.exec_driver_sql("PRAGMA table_info(orders)").fetchall()}
        if "discount_type" not in ocols:
            conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN discount_type VARCHAR(20)")
        if "discount_amount" not in ocols:
            conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN discount_amount FLOAT DEFAULT 0.0")
        if "applied_coupon_id" not in ocols:
            conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN applied_coupon_id INTEGER")
        if "deleted_by_user" not in ocols:
            conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN deleted_by_user BOOLEAN DEFAULT 0")
        if "deleted_at" not in ocols:
            conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN deleted_at DATETIME")
        ccols = {r[1] for r in conn.exec_driver_sql("PRAGMA table_info(coupons)").fetchall()}
        if "allowed_product_id" not in ccols:
            conn.exec_driver_sql("ALTER TABLE coupons ADD COLUMN allowed_product_id INTEGER")
        
        # 检查并更新 knowledge_documents 表
        try:
            kdcols = {r[1] for r in conn.exec_driver_sql("PRAGMA table_info(knowledge_documents)").fetchall()}
            if "metadata" not in kdcols:
                conn.exec_driver_sql("ALTER TABLE knowledge_documents ADD COLUMN metadata TEXT")
            if "quality_score" not in kdcols:
                conn.exec_driver_sql("ALTER TABLE knowledge_documents ADD COLUMN quality_score FLOAT")
        except Exception:
            pass  # 表可能不存在，会在首次创建时自动创建
        
        cnt = conn.exec_driver_sql("SELECT COUNT(1) FROM membership_plans").scalar()
        if not cnt:
            conn.exec_driver_sql(
                "INSERT INTO membership_plans(code,name,discount_percent,active) VALUES"
                "('standard_plan','标准会员计划',5,1),"
                "('premium_plan','高级会员计划',10,1)"
            )

    app = FastAPI(title="智慧商城 API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 静态文件（聊天附件）
    BASE_DIR = Path(__file__).resolve().parent
    STATIC_DIR = BASE_DIR / "static"
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "uploads").mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.include_router(users_route.router)
    app.include_router(products_route.router)
    app.include_router(cart_route.router)
    app.include_router(orders_route.router)
    app.include_router(logistics_route.router)
    app.include_router(addresses_route.router)
    app.include_router(memberships_route.router)
    app.include_router(coupons_route.router)
    app.include_router(customer_service_route.router)
    app.include_router(knowledge_base_route.router)  # 知识库管理路由（管理员接口）
    app.include_router(admin_router)

    # 初始化优惠券自动发放服务
    try:
        from .services.coupon_auto_issue_service import get_auto_issue_service
        from .database import get_db
        
        auto_issue_service = get_auto_issue_service()
        if auto_issue_service.enabled and auto_issue_service.scheduler:
            # 设置定时任务（每日检查）
            def get_db_session():
                from .database import SessionLocal
                return SessionLocal()
            
            auto_issue_service.schedule_daily_check(get_db_session)
            print("✓ 优惠券自动发放定时任务已启动")
    except Exception as e:
        print(f"⚠ 优惠券自动发放服务初始化失败: {e}")
    
    # 初始化 Redis 缓存服务
    try:
        from .services.cache_service import get_cache_service
        cache_service = get_cache_service()
        if cache_service.enabled:
            print("✓ Redis 缓存服务已初始化")
    except Exception as e:
        print(f"⚠ Redis 缓存服务初始化失败: {e}")

    @app.get("/")
    def read_root():
        return {"message": "智慧商城后端服务运行中"}

    @app.on_event("shutdown")
    def shutdown_event():
        """应用关闭时清理资源"""
        try:
            from .services.coupon_auto_issue_service import get_auto_issue_service
            auto_issue_service = get_auto_issue_service()
            if auto_issue_service:
                auto_issue_service.shutdown()
        except Exception:
            pass

    return app


app = create_app()

