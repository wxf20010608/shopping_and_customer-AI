"""
优惠券自动发放服务
支持多种自动发放规则：新用户注册、首次购买、生日等
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from ..models import Coupon, UserCoupon, User, Order
from ..utils import load_env


class CouponAutoIssueService:
    """优惠券自动发放服务类"""
    
    def __init__(self):
        load_env()
        self.scheduler = None
        self.enabled = os.environ.get("COUPON_AUTO_ISSUE_ENABLED", "true").lower() == "true"
        self.rules: Dict[str, Dict] = {}  # 存储自动发放规则
        
        if self.enabled:
            try:
                self.scheduler = BackgroundScheduler()
                self.scheduler.start()
                print("✓ 优惠券自动发放服务已启动")
            except Exception as e:
                print(f"⚠ 启动定时任务失败: {e}")
                self.scheduler = None
    
    def register_rule(self, rule_id: str, rule: Dict[str, Any]):
        """注册自动发放规则
        
        参数:
        - rule_id: 规则ID
        - rule: 规则配置
            - trigger: 触发器类型 ('register', 'first_order', 'birthday', 'cron', 'date')
            - coupon_id: 优惠券ID
            - condition: 条件（可选）
            - cron: Cron表达式（cron触发器时需要）
        """
        self.rules[rule_id] = rule
    
    def issue_to_new_user(self, db: Session, user_id: int, coupon_id: int) -> bool:
        """给新注册用户发放优惠券"""
        try:
            # 检查用户是否已经领取过该优惠券
            existing = db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id
            ).first()
            if existing:
                return False
            
            # 检查优惠券是否存在且有效
            coupon = db.query(Coupon).filter(
                Coupon.id == coupon_id,
                Coupon.active == True
            ).first()
            if not coupon:
                return False
            
            # 发放优惠券
            user_coupon = UserCoupon(
                user_id=user_id,
                coupon_id=coupon_id,
                status="unused"
            )
            db.add(user_coupon)
            db.commit()
            print(f"✓ 新用户 {user_id} 自动发放优惠券 {coupon_id} ({coupon.code})")
            return True
        except Exception as e:
            db.rollback()
            print(f"⚠ 新用户发放优惠券失败: {e}")
            return False
    
    def issue_to_first_order_user(self, db: Session, user_id: int, coupon_id: int) -> bool:
        """给首次购买用户发放优惠券"""
        try:
            # 检查用户是否已有订单
            order_count = db.query(Order).filter(Order.user_id == user_id).count()
            if order_count != 1:  # 必须正好是第一个订单
                return False
            
            # 检查是否已经领取过该优惠券
            existing = db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id
            ).first()
            if existing:
                return False
            
            # 检查优惠券是否存在且有效
            coupon = db.query(Coupon).filter(
                Coupon.id == coupon_id,
                Coupon.active == True
            ).first()
            if not coupon:
                return False
            
            # 发放优惠券
            user_coupon = UserCoupon(
                user_id=user_id,
                coupon_id=coupon_id,
                status="unused"
            )
            db.add(user_coupon)
            db.commit()
            print(f"✓ 首次购买用户 {user_id} 自动发放优惠券 {coupon_id} ({coupon.code})")
            return True
        except Exception as e:
            db.rollback()
            print(f"⚠ 首次购买用户发放优惠券失败: {e}")
            return False
    
    def issue_birthday_coupon(self, db: Session, user_id: int, coupon_id: int) -> bool:
        """给生日用户发放优惠券"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # 这里简化处理，实际应该根据用户的生日字段判断
            # 假设每月检查一次，为当月生日的用户发放
            # 实际实现需要添加生日字段到用户表
            
            # 检查是否已经领取过该优惠券（本月）
            today = datetime.utcnow()
            this_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            existing = db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id,
                UserCoupon.created_at >= this_month_start
            ).first()
            if existing:
                return False
            
            # 检查优惠券是否存在且有效
            coupon = db.query(Coupon).filter(
                Coupon.id == coupon_id,
                Coupon.active == True
            ).first()
            if not coupon:
                return False
            
            # 发放优惠券
            user_coupon = UserCoupon(
                user_id=user_id,
                coupon_id=coupon_id,
                status="unused"
            )
            db.add(user_coupon)
            db.commit()
            print(f"✓ 生日用户 {user_id} 自动发放优惠券 {coupon_id} ({coupon.code})")
            return True
        except Exception as e:
            db.rollback()
            print(f"⚠ 生日用户发放优惠券失败: {e}")
            return False
    
    def schedule_daily_check(self, db_factory):
        """定时任务：每日检查自动发放规则"""
        if not self.scheduler:
            return
        
        def daily_task():
            try:
                db = db_factory()
                # 这里可以添加每日检查逻辑
                # 例如：检查生日用户、检查首次购买用户等
                db.close()
            except Exception as e:
                print(f"⚠ 定时任务执行失败: {e}")
        
        # 每天凌晨1点执行
        self.scheduler.add_job(
            daily_task,
            trigger=CronTrigger(hour=1, minute=0),
            id="daily_coupon_check",
            replace_existing=True
        )
        print("✓ 已添加每日优惠券检查定时任务（每天 01:00）")
    
    def shutdown(self):
        """关闭定时任务调度器"""
        if self.scheduler:
            self.scheduler.shutdown()
            print("✓ 优惠券自动发放服务已关闭")


# 全局服务实例
_auto_issue_service = None


def get_auto_issue_service() -> CouponAutoIssueService:
    """获取优惠券自动发放服务实例（单例模式）"""
    global _auto_issue_service
    if _auto_issue_service is None:
        _auto_issue_service = CouponAutoIssueService()
    return _auto_issue_service
