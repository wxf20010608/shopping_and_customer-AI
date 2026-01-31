import sys
import os
# 兼容宝塔等直接运行 app/main.py：把 backend 加入 path，避免 "No module named 'app'"
_backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.utils import load_env
from app.routers import (
    cart_route,
    logistics_route,
    orders_route,
    products_route,
    users_route,
)
from app.routers import addresses_route, memberships_route, coupons_route, customer_service_route
from app.routers import knowledge_base_route, reviews_route
from app.admin_router import admin_router


def create_app() -> FastAPI:
    load_env()
    
    # 配置日志记录到文件
    try:
        from app.services.logging_config import setup_logging
        log_dir = os.environ.get("LOG_DIR")
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        setup_logging(log_dir=log_dir, log_level=log_level)
    except Exception as e:
        print(f"⚠ 日志配置失败: {e}")
    
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
        
        # 检查并创建 reviews 表（商品评价）
        try:
            rcols = {r[1] for r in conn.exec_driver_sql("PRAGMA table_info(reviews)").fetchall()}
        except Exception:
            rcols = set()
        # 如果表不存在，会在首次创建时自动创建（通过 SQLAlchemy Base.metadata.create_all）
        
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

    # 管理员/知识库/评价路由依赖 admin_router（含 stock_alert_service），缺失时跳过
    try:
        from app.admin_router import admin_router
        from app.routers import knowledge_base_route, reviews_route
        app.include_router(knowledge_base_route.router)
        app.include_router(reviews_route.router)
        app.include_router(admin_router)
    except ModuleNotFoundError as e:
        print(f"⚠ 管理员/知识库/评价路由未加载（缺少依赖，如 stock_alert_service）: {e}")

    # 初始化优惠券自动发放服务
    try:
        from app.services.coupon_auto_issue_service import get_auto_issue_service
        from app.database import get_db
        
        auto_issue_service = get_auto_issue_service()
        if auto_issue_service.enabled and auto_issue_service.scheduler:
            # 设置定时任务（每日检查）
            def get_db_session():
                from app.database import SessionLocal
                return SessionLocal()
            
            auto_issue_service.schedule_daily_check(get_db_session)
            print("✓ 优惠券自动发放定时任务已启动")
    except Exception as e:
        print(f"⚠ 优惠券自动发放服务初始化失败: {e}")
    
    # 初始化 Redis 缓存服务
    try:
        from app.services.cache_service import get_cache_service
        cache_service = get_cache_service()
        if cache_service.enabled:
            print("✓ Redis 缓存服务已初始化")
    except Exception as e:
        print(f"⚠ Redis 缓存服务初始化失败: {e}")
    
    # 后台异步初始化 RAG 服务（避免阻塞启动和首次请求）
    import threading
    def init_rag_background():
        try:
            from app.services.rag_service import get_rag_service
            print("🔄 后台初始化 RAG 服务...")
            rag_service = get_rag_service()
            if rag_service and rag_service.embedding_model:
                print("✓ RAG 服务后台初始化完成")
            else:
                print("⚠ RAG 服务初始化完成但嵌入模型未加载")
        except Exception as e:
            print(f"⚠ RAG 服务后台初始化失败: {e}")
    
    rag_thread = threading.Thread(target=init_rag_background, daemon=True)
    rag_thread.start()
    print("✓ RAG 服务后台初始化已启动")

    @app.get("/")
    def read_root():
        return {"message": "智慧商城后端服务运行中"}

    @app.on_event("shutdown")
    def shutdown_event():
        """应用关闭时清理资源"""
        try:
            from app.services.coupon_auto_issue_service import get_auto_issue_service
            auto_issue_service = get_auto_issue_service()
            if auto_issue_service:
                auto_issue_service.shutdown()
        except Exception:
            pass

    return app


app = create_app()

