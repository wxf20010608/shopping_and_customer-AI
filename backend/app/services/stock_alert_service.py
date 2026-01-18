"""
商品库存预警服务
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Product
from ..utils import load_env


class StockAlertService:
    """库存预警服务类"""
    
    def __init__(self):
        load_env()
        self.enabled = os.environ.get("STOCK_ALERT_ENABLED", "true").lower() == "true"
        self.alert_threshold = int(os.environ.get("STOCK_ALERT_THRESHOLD", "10"))  # 默认预警阈值：10
    
    def check_low_stock_products(self, db: Session, threshold: Optional[int] = None) -> List[Dict]:
        """检查低库存商品"""
        if not self.enabled:
            return []
        
        alert_threshold = threshold or self.alert_threshold
        
        products = (
            db.query(Product)
            .filter(Product.stock <= alert_threshold)
            .order_by(Product.stock.asc())
            .all()
        )
        
        alerts = []
        for product in products:
            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock,
                "threshold": alert_threshold,
                "category": product.category,
                "alert_level": self._get_alert_level(product.stock),
                "created_at": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _get_alert_level(self, stock: int) -> str:
        """获取预警级别"""
        if stock == 0:
            return "critical"  # 缺货
        elif stock <= 3:
            return "high"  # 高预警
        elif stock <= 5:
            return "medium"  # 中预警
        else:
            return "low"  # 低预警
    
    def get_stock_statistics(self, db: Session) -> Dict:
        """获取库存统计"""
        total_products = db.query(func.count(Product.id)).scalar()
        low_stock_count = db.query(func.count(Product.id)).filter(
            Product.stock <= self.alert_threshold
        ).scalar()
        out_of_stock_count = db.query(func.count(Product.id)).filter(
            Product.stock == 0
        ).scalar()
        
        total_stock = db.query(func.sum(Product.stock)).scalar() or 0
        
        return {
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "total_stock": total_stock,
            "alert_threshold": self.alert_threshold
        }


# 全局服务实例
_stock_alert_service = None


def get_stock_alert_service() -> StockAlertService:
    """获取库存预警服务实例（单例模式）"""
    global _stock_alert_service
    if _stock_alert_service is None:
        _stock_alert_service = StockAlertService()
    return _stock_alert_service
