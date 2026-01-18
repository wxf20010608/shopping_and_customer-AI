"""
Redis 缓存服务
提供统一的缓存接口，优化数据库查询性能
"""
import json
import os
from typing import Optional, Any
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..utils import load_env


class CacheService:
    """Redis 缓存服务类"""
    
    def __init__(self):
        load_env()
        self.redis_client = None
        self.enabled = os.environ.get("REDIS_ENABLED", "true").lower() == "true"
        
        if self.enabled and REDIS_AVAILABLE:
            try:
                redis_host = os.environ.get("REDIS_HOST", "localhost")
                redis_port = int(os.environ.get("REDIS_PORT", "6379"))
                redis_db = int(os.environ.get("REDIS_DB", "0"))
                redis_password = os.environ.get("REDIS_PASSWORD")
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # 测试连接
                self.redis_client.ping()
                print(f"✓ Redis 缓存已启用 (host={redis_host}, port={redis_port}, db={redis_db})")
            except Exception as e:
                print(f"⚠ Redis 连接失败，缓存功能将禁用: {e}")
                self.redis_client = None
                self.enabled = False
        else:
            if not REDIS_AVAILABLE:
                print("ℹ Redis 库未安装，缓存功能将禁用")
            else:
                print("ℹ Redis 已配置为禁用状态")
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        parts = [prefix]
        if args:
            parts.extend(str(arg) for arg in args)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            parts.extend(f"{k}={v}" for k, v in sorted_kwargs)
        return ":".join(parts)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.enabled or not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"⚠ 读取缓存失败 (key={key}): {e}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.enabled or not self.redis_client:
            return False
        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            if expire:
                self.redis_client.setex(key, expire, serialized)
            else:
                self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            print(f"⚠ 写入缓存失败 (key={key}): {e}")
            return False
    
    def delete(self, *keys: str) -> int:
        """删除缓存键"""
        if not self.enabled or not self.redis_client:
            return 0
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"⚠ 删除缓存失败 (keys={keys}): {e}")
            return 0
    
    def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存键"""
        if not self.enabled or not self.redis_client:
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"⚠ 按模式删除缓存失败 (pattern={pattern}): {e}")
            return 0
    
    def clear(self) -> bool:
        """清空所有缓存"""
        if not self.enabled or not self.redis_client:
            return False
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"⚠ 清空缓存失败: {e}")
            return False
    
    # 便捷方法：常用缓存键生成
    def cache_product(self, product_id: int, value: Any, expire: int = 3600) -> bool:
        """缓存商品信息"""
        key = self._make_key("product", product_id)
        return self.set(key, value, expire)
    
    def get_product(self, product_id: int) -> Optional[Any]:
        """获取缓存的商品信息"""
        key = self._make_key("product", product_id)
        return self.get(key)
    
    def delete_product(self, product_id: int):
        """删除商品缓存"""
        key = self._make_key("product", product_id)
        self.delete(key)
        # 同时删除相关列表缓存
        self.delete_pattern("product:list:*")
    
    def cache_product_list(self, search: Optional[str], category: Optional[str], 
                          page: int, page_size: int, value: Any, expire: int = 300) -> bool:
        """缓存商品列表"""
        key = self._make_key("product:list", search=search, category=category, 
                            page=page, page_size=page_size)
        return self.set(key, value, expire)
    
    def get_product_list(self, search: Optional[str], category: Optional[str],
                        page: int, page_size: int) -> Optional[Any]:
        """获取缓存的商品列表"""
        key = self._make_key("product:list", search=search, category=category,
                            page=page, page_size=page_size)
        return self.get(key)
    
    def cache_user(self, user_id: int, value: Any, expire: int = 1800) -> bool:
        """缓存用户信息"""
        key = self._make_key("user", user_id)
        return self.set(key, value, expire)
    
    def get_user(self, user_id: int) -> Optional[Any]:
        """获取缓存的用户信息"""
        key = self._make_key("user", user_id)
        return self.get(key)
    
    def delete_user(self, user_id: int):
        """删除用户缓存"""
        key = self._make_key("user", user_id)
        self.delete(key)
        # 删除用户相关的其他缓存
        self.delete_pattern(f"user:{user_id}:*")
    
    def cache_categories(self, value: Any, expire: int = 3600) -> bool:
        """缓存商品分类列表"""
        key = self._make_key("categories")
        return self.set(key, value, expire)
    
    def get_categories(self) -> Optional[Any]:
        """获取缓存的商品分类列表"""
        key = self._make_key("categories")
        return self.get(key)
    
    def delete_categories(self):
        """删除商品分类缓存"""
        key = self._make_key("categories")
        self.delete(key)


# 全局缓存服务实例
_cache_service = None


def get_cache_service() -> CacheService:
    """获取缓存服务实例（单例模式）"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
