#!/usr/bin/env python
"""
检查数据库状态和表结构的脚本
用于验证数据库是否正确更新
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'smart_mall.db'

def check_database():
    """检查数据库状态"""
    print("=" * 60)
    print("数据库状态检查")
    print("=" * 60)
    print()
    
    # 检查文件是否存在
    if not DB_PATH.exists():
        print(f"✗ 数据库文件不存在: {DB_PATH}")
        return
    
    # 文件信息
    stat = DB_PATH.stat()
    print(f"数据库文件路径: {DB_PATH}")
    print(f"文件大小: {stat.st_size / 1024 / 1024:.2f} MB")
    print(f"最后修改时间: {datetime.fromtimestamp(stat.st_mtime)}")
    print()
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✓ 数据库连接成功")
        print(f"✓ 数据库表数量: {len(tables)}")
        print()
        print("数据库表列表:")
        for i, table in enumerate(tables, 1):
            # 获取每个表的列数
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            # 获取每个表的行数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
            except:
                count = 0
            print(f"  {i:2d}. {table:20s} - {len(columns):2d} 列, {count:6d} 行")
        
        print()
        
        # 检查关键表的结构
        print("关键表结构检查:")
        key_tables = ['orders', 'memberships', 'coupons', 'membership_cards']
        for table in key_tables:
            if table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"  {table}:")
                print(f"    列: {', '.join(columns)}")
        
        # 检查 orders 表是否有新字段
        if 'orders' in tables:
            print()
            print("Orders 表字段检查:")
            cursor.execute("PRAGMA table_info(orders)")
            orders_columns = [col[1] for col in cursor.fetchall()]
            expected_new_columns = ['discount_type', 'discount_amount', 'applied_coupon_id', 'deleted_by_user', 'deleted_at']
            for col in expected_new_columns:
                if col in orders_columns:
                    print(f"  ✓ {col} - 已存在")
                else:
                    print(f"  ✗ {col} - 缺失")
        
        conn.close()
        print()
        print("=" * 60)
        print("✓ 数据库检查完成")
        print("=" * 60)
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print(f"✗ 数据库文件被锁定！")
            print("  可能的原因：")
            print("  1. FastAPI 后端服务正在运行")
            print("  2. Navicat 正在打开该数据库")
            print("  3. 其他程序正在使用该数据库")
            print()
            print("  解决方法：")
            print("  1. 关闭 FastAPI 后端服务")
            print("  2. 关闭 Navicat 中对该数据库的连接")
            print("  3. 重新运行此检查脚本")
        else:
            print(f"✗ 数据库访问错误: {e}")
    except Exception as e:
        print(f"✗ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
