"""
数据统计和分析服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract

from ..models import Order, OrderItem, Product, User, Review, Coupon


class StatisticsService:
    """数据统计服务类"""
    
    def get_dashboard_stats(self, db: Session) -> Dict:
        """获取仪表板统计（概览）"""
        # 订单统计
        total_orders = db.query(func.count(Order.id)).scalar()
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.status.in_(["paid", "shipped", "completed"])
        ).scalar() or 0.0
        
        # 今日订单
        today = datetime.utcnow().date()
        today_orders = db.query(func.count(Order.id)).filter(
            func.date(Order.created_at) == today
        ).scalar()
        today_revenue = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today,
            Order.status.in_(["paid", "shipped", "completed"])
        ).scalar() or 0.0
        
        # 用户统计
        total_users = db.query(func.count(User.id)).scalar()
        new_users_today = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == today
        ).scalar()
        
        # 商品统计
        total_products = db.query(func.count(Product.id)).scalar()
        low_stock_products = db.query(func.count(Product.id)).filter(
            Product.stock <= 10
        ).scalar()
        
        # 评价统计
        total_reviews = db.query(func.count(Review.id)).filter(
            Review.status == "approved"
        ).scalar()
        
        # 优惠券统计
        total_coupons = db.query(func.count(Coupon.id)).filter(
            Coupon.active == True
        ).scalar()
        
        # 热门商品（销量前5）
        top_5_products_query = (
            db.query(
                Product.name,
                func.sum(OrderItem.quantity).label("quantity_sold")
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status.in_(["paid", "shipped", "completed"]))
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(5)
            .all()
        )
        
        top_5_products = [
            {"name": p.name, "quantity_sold": p.quantity_sold or 0}
            for p in top_5_products_query
        ]
        
        # 近7天订单量
        seven_days_ago = today - timedelta(days=7)
        recent_orders_7_days = db.query(func.count(Order.id)).filter(
            func.date(Order.created_at) >= seven_days_ago
        ).scalar()
        
        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_sales_amount": round(total_revenue, 2),
            "recent_orders_7_days": recent_orders_7_days,
            "top_5_products": top_5_products
        }
    
    def get_sales_statistics(self, db: Session, days: int = 30) -> Dict:
        """获取销售统计（按日期）"""
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        # 按日期统计订单和销售额
        daily_stats = (
            db.query(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.total_amount).label("revenue")
            )
            .filter(
                Order.created_at >= start_date,
                Order.status.in_(["paid", "shipped", "completed"])
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )
        
        data = []
        for stat in daily_stats:
            # 处理日期：可能是 date 对象或字符串
            date_str = None
            if stat.date:
                if isinstance(stat.date, str):
                    date_str = stat.date
                elif hasattr(stat.date, 'isoformat'):
                    date_str = stat.date.isoformat()
                else:
                    # 尝试转换为字符串
                    date_str = str(stat.date)
            
            data.append({
                "date": date_str,
                "orders": stat.order_count,
                "amount": round(stat.revenue or 0.0, 2)
            })
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().date().isoformat(),
            "data": data
        }
    
    def get_product_statistics(self, db: Session) -> Dict:
        """获取商品销售统计"""
        # 最畅销商品（按销量）
        top_products = (
            db.query(
                Product.id,
                Product.name,
                Product.category,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue")
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status.in_(["paid", "shipped", "completed"]))
            .group_by(Product.id, Product.name, Product.category)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(10)
            .all()
        )
        
        top_products_data = []
        for prod in top_products:
            top_products_data.append({
                "product_id": prod.id,
                "name": prod.name,
                "category": prod.category,
                "quantity_sold": prod.total_sold or 0,
                "sales_amount": round(prod.total_revenue or 0.0, 2)
            })
        
        # 按分类统计
        category_stats = (
            db.query(
                Product.category,
                func.count(Product.id).label("product_count"),
                func.sum(OrderItem.quantity).label("total_sold")
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status.in_(["paid", "shipped", "completed"]))
            .group_by(Product.category)
            .order_by(func.sum(OrderItem.quantity).desc())
            .all()
        )
        
        category_data = []
        for stat in category_stats:
            category_data.append({
                "category": stat.category or "未分类",
                "product_count": stat.product_count or 0,
                "total_sold": stat.total_sold or 0
            })
        
        return {
            "top_products": top_products_data,
            "category_statistics": category_data
        }
    
    def get_user_statistics(self, db: Session) -> Dict:
        """获取用户统计"""
        # 用户注册趋势（按月份）
        monthly_registrations = (
            db.query(
                extract("year", User.created_at).label("year"),
                extract("month", User.created_at).label("month"),
                func.count(User.id).label("user_count")
            )
            .group_by(extract("year", User.created_at), extract("month", User.created_at))
            .order_by(extract("year", User.created_at).desc(), extract("month", User.created_at).desc())
            .limit(12)
            .all()
        )
        
        monthly_data = []
        for stat in monthly_registrations:
            monthly_data.append({
                "year": int(stat.year),
                "month": int(stat.month),
                "user_count": stat.user_count
            })
        
        # 活跃用户（有订单的用户）
        active_users = db.query(func.count(func.distinct(Order.user_id))).scalar()
        
        # 总用户数
        total_users = db.query(func.count(User.id)).scalar()
        
        # 今日新增用户
        today = datetime.utcnow().date()
        new_users_today = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == today
        ).scalar()
        
        # 近7天活跃用户（有订单的用户）
        seven_days_ago = today - timedelta(days=7)
        active_users_7_days = db.query(func.count(func.distinct(Order.user_id))).filter(
            func.date(Order.created_at) >= seven_days_ago
        ).scalar()
        
        return {
            "total_users": total_users,
            "new_users_today": new_users_today,
            "active_users_7_days": active_users_7_days,
            "monthly_registrations": monthly_data,
            "active_users": active_users
        }


# 全局服务实例
_statistics_service = None


def get_statistics_service() -> StatisticsService:
    """获取数据统计服务实例（单例模式）"""
    global _statistics_service
    if _statistics_service is None:
        _statistics_service = StatisticsService()
    return _statistics_service
