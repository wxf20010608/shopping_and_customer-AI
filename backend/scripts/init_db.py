#!/usr/bin/env python
"""
数据库初始化脚本
用于创建和更新数据库结构
运行方式: python init_db.py (需要在 backend 目录下运行)
"""
import sys
from pathlib import Path

# 添加项目路径到 Python 路径
# 脚本在 backend 目录，直接添加当前目录到路径
backend_root = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_root))

from app.database import Base, engine
from app.models import (
    User, Product, Cart, CartItem, Order, OrderItem,
    Address, Category, Membership, MembershipPlan, MembershipCard,
    Coupon, UserCoupon, ShippingInfo, ChatMessage
)
from datetime import datetime


def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")


def update_schema():
    """更新数据库结构（添加缺失的列）"""
    print("正在检查并更新数据库结构...")
    
    with engine.connect() as conn:
        # 检查并更新 memberships 表
        try:
            rows = conn.exec_driver_sql("PRAGMA table_info(memberships)").fetchall()
            names = {r[1] for r in rows}
            if "plan_id" not in names:
                print("  添加 memberships.plan_id 列...")
                conn.exec_driver_sql("ALTER TABLE memberships ADD COLUMN plan_id INTEGER")
                print("  ✓ memberships.plan_id 添加完成")
        except Exception as e:
            print(f"  ⚠ 更新 memberships 表时出错: {e}")
        
        # 检查并更新 membership_cards 表
        try:
            rows = conn.exec_driver_sql("PRAGMA table_info(membership_cards)").fetchall()
            names = {r[1] for r in rows}
            if "published" not in names:
                print("  添加 membership_cards.published 列...")
                conn.exec_driver_sql("ALTER TABLE membership_cards ADD COLUMN published BOOLEAN DEFAULT 1")
                print("  ✓ membership_cards.published 添加完成")
        except Exception as e:
            print(f"  ⚠ 更新 membership_cards 表时出错: {e}")
        
        # 检查并更新 orders 表
        try:
            rows = conn.exec_driver_sql("PRAGMA table_info(orders)").fetchall()
            names = {r[1] for r in rows}
            
            if "discount_type" not in names:
                print("  添加 orders.discount_type 列...")
                conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN discount_type VARCHAR(20)")
                print("  ✓ orders.discount_type 添加完成")
            
            if "discount_amount" not in names:
                print("  添加 orders.discount_amount 列...")
                conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN discount_amount FLOAT DEFAULT 0.0")
                print("  ✓ orders.discount_amount 添加完成")
            
            if "applied_coupon_id" not in names:
                print("  添加 orders.applied_coupon_id 列...")
                conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN applied_coupon_id INTEGER")
                print("  ✓ orders.applied_coupon_id 添加完成")
            
            if "deleted_by_user" not in names:
                print("  添加 orders.deleted_by_user 列...")
                conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN deleted_by_user BOOLEAN DEFAULT 0")
                print("  ✓ orders.deleted_by_user 添加完成")
            
            if "deleted_at" not in names:
                print("  添加 orders.deleted_at 列...")
                conn.exec_driver_sql("ALTER TABLE orders ADD COLUMN deleted_at DATETIME")
                print("  ✓ orders.deleted_at 添加完成")
        except Exception as e:
            print(f"  ⚠ 更新 orders 表时出错: {e}")
        
        # 检查并更新 coupons 表
        try:
            rows = conn.exec_driver_sql("PRAGMA table_info(coupons)").fetchall()
            names = {r[1] for r in rows}
            if "allowed_product_id" not in names:
                print("  添加 coupons.allowed_product_id 列...")
                conn.exec_driver_sql("ALTER TABLE coupons ADD COLUMN allowed_product_id INTEGER")
                print("  ✓ coupons.allowed_product_id 添加完成")
        except Exception as e:
            print(f"  ⚠ 更新 coupons 表时出错: {e}")
        
        # 检查并更新 knowledge_documents 表
        try:
            rows = conn.exec_driver_sql("PRAGMA table_info(knowledge_documents)").fetchall()
            names = {r[1] for r in rows}
            
            if "metadata" not in names:
                print("  添加 knowledge_documents.metadata 列...")
                conn.exec_driver_sql("ALTER TABLE knowledge_documents ADD COLUMN metadata TEXT")
                print("  ✓ knowledge_documents.metadata 添加完成")
            
            if "quality_score" not in names:
                print("  添加 knowledge_documents.quality_score 列...")
                conn.exec_driver_sql("ALTER TABLE knowledge_documents ADD COLUMN quality_score FLOAT")
                print("  ✓ knowledge_documents.quality_score 添加完成")
        except Exception as e:
            # 表可能不存在，这是正常的（首次创建时会自动创建）
            pass
        
        conn.commit()
    
    print("✓ 数据库结构更新完成")


def init_base_data():
    """初始化基础数据"""
    print("正在初始化基础数据...")
    
    try:
        with engine.connect() as conn:
            # 初始化会员计划
            cnt = conn.exec_driver_sql("SELECT COUNT(1) FROM membership_plans").scalar()
            if not cnt:
                print("  初始化会员计划数据...")
                now = datetime.utcnow().isoformat()
                conn.exec_driver_sql(
                    f"INSERT INTO membership_plans(code, name, discount_percent, active, created_at, updated_at) VALUES "
                    f"('standard_plan', '标准会员计划', 5, 1, '{now}', '{now}'),"
                    f"('premium_plan', '高级会员计划', 10, 1, '{now}', '{now}')"
                )
                conn.commit()
                print("  ✓ 会员计划数据初始化完成")
            else:
                print("  ✓ 会员计划数据已存在，跳过初始化")
    except Exception as e:
        print(f"  ⚠ 初始化基础数据时出错: {e}")
        import traceback
        traceback.print_exc()


def verify_database():
    """验证数据库结构"""
    print("正在验证数据库结构...")
    
    expected_tables = [
        'users', 'products', 'categories', 'carts', 'cart_items',
        'orders', 'order_items', 'addresses', 'shipping_info',
        'memberships', 'membership_plans', 'membership_cards',
        'coupons', 'user_coupons', 'chat_messages'
    ]
    
    with engine.connect() as conn:
        result = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        existing_tables = {row[0] for row in result}
        
        missing_tables = set(expected_tables) - existing_tables
        if missing_tables:
            print(f"  ⚠ 缺少以下表: {', '.join(missing_tables)}")
        else:
            print(f"  ✓ 所有预期的表都已存在 ({len(existing_tables)} 个)")
        
        print(f"  数据库表列表: {', '.join(sorted(existing_tables))}")


def main():
    """主函数"""
    print("=" * 60)
    print("智慧商城 - 数据库初始化脚本")
    print("=" * 60)
    print()
    
    try:
        # 1. 创建表
        create_tables()
        print()
        
        # 2. 更新结构
        update_schema()
        print()
        
        # 3. 初始化基础数据
        init_base_data()
        print()
        
        # 4. 验证数据库
        verify_database()
        print()
        
        print("=" * 60)
        print("✓ 数据库初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 数据库初始化失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
