from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from .. import schemas
from ..models import Product, Category
import random
import uuid
import hashlib


def _generate_image_url_from_name(name: str, category: Optional[str] = None, product_id: Optional[int] = None) -> str:
    """根据商品名称生成固定的图片URL，确保每个商品名称对应唯一且固定的图片"""
    # 分类到图片关键字映射
    category_to_slug = {
        "手机": "phone",
        "电脑": "laptop",
        "家电": "appliance",
        "服饰": "clothing",
        "鞋靴": "shoes",
        "美妆": "cosmetics",
        "食品": "food",
        "图书": "book",
        "运动": "sport",
        "母婴": "baby",
        "家具": "furniture",
        "汽车": "car",
        "玩具": "toy",
        "数码": "camera",
        "户外": "outdoor",
        "宠物": "pet",
        "手表": "watch",
        "珠宝": "jewelry",
    }
    slug = category_to_slug.get(category, "product") if category else "product"
    
    # 如果有商品ID，使用ID确保唯一性；否则使用名称的完整哈希值
    if product_id:
        # 使用商品ID作为lock值，确保每个商品对应唯一的图片
        lock_value = product_id
    else:
        # 使用商品名称的完整MD5哈希值，将32位十六进制转换为整数
        # 使用前16位和后16位分别计算，然后组合，确保更大的数值范围
        name_hash_full = hashlib.md5(name.encode('utf-8')).hexdigest()
        lock_value = int(name_hash_full[:16], 16) + int(name_hash_full[16:], 16)
    
    return f"https://loremflickr.com/640/480/{slug}?lock={lock_value}"

def create_product(payload: schemas.ProductCreate, db: Session) -> Product:
    product_data = payload.model_dump()
    # 如果没有提供图片URL，先创建商品获取ID，然后根据商品名称和ID生成图片
    if not product_data.get('image_url'):
        # 先创建商品以获取ID
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        # 使用商品ID和名称生成固定的图片URL
        product.image_url = _generate_image_url_from_name(
            product.name,
            product.category,
            product.id
        )
        db.commit()
        db.refresh(product)
        return product
    else:
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product


# 修改：增加 category 精确筛选，并支持分页
# NOTE: 增加分页参数 page, page_size，返回 ProductPage
# 默认每页10条

# 分页查询

def list_products(search: Optional[str], category: Optional[str], db: Session, page: int = 1, page_size: int = 10, random_order: bool = True) -> schemas.ProductPage:
    """
    获取商品列表（支持随机排序，保证每次刷新顺序不同）
    
    参数:
    - search: 搜索关键词
    - category: 分类筛选
    - page: 页码
    - page_size: 每页数量
    - random_order: 是否随机排序（默认True，每次刷新顺序不同）
    """
    query = db.query(Product)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(like_pattern)) | (Product.category.ilike(like_pattern))
        )
    if category:
        query = query.filter(Product.category == category)
    total = query.count()
    
    # 根据 random_order 参数决定排序方式
    if random_order:
        # 使用 SQLite 的 RANDOM() 函数进行随机排序
        # 这样每次刷新页面时，商品顺序都会不同
        # 使用 text() 确保与 SQLite 兼容
        items = (
            query.order_by(text("RANDOM()"))
            .offset((max(page, 1) - 1) * max(page_size, 1))
            .limit(max(page_size, 1))
            .all()
        )
    else:
        # 如果不使用随机排序，按创建时间倒序（默认排序）
        items = (
            query.order_by(Product.created_at.desc())
            .offset((max(page, 1) - 1) * max(page_size, 1))
            .limit(max(page_size, 1))
            .all()
        )
    
    # 确保所有商品的图片URL都是基于名称和ID的固定格式
    need_update = False
    for item in items:
        if not item.image_url or (item.image_url and 'loremflickr.com' in item.image_url and f'lock={item.id}' not in item.image_url):
            item.image_url = _generate_image_url_from_name(item.name, item.category, item.id)
            need_update = True
    # 批量提交更新，提高性能
    if need_update:
        db.commit()
        for item in items:
            db.refresh(item)
    
    return schemas.ProductPage(items=items, total=total, page=max(page, 1), page_size=max(page_size, 1))


def get_product(product_id: int, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    # 如果图片URL不存在或者是旧的随机格式，自动更新为基于名称和ID的固定图片
    if not product.image_url or (product.image_url and 'loremflickr.com' in product.image_url and f'lock={product_id}' not in product.image_url):
        product.image_url = _generate_image_url_from_name(product.name, product.category, product.id)
        db.commit()
        db.refresh(product)
    return product


def get_customer_service(product_id: int, db: Session) -> schemas.CustomerServiceResponse:
    product_exists = db.query(Product.id).filter(Product.id == product_id).first()
    if not product_exists:
        raise HTTPException(status_code=404, detail="商品不存在")

    return schemas.CustomerServiceResponse(
        product_id=product_id,
        channels=[
            {
                "channel": "online_chat",
                "description": "在线客服接入接口，请由客服系统调用 /api/customer-service/chat",
                "external_api": "/api/customer-service/chat",
            },
            {
                "channel": "phone",
                "description": "电话客服，由客服系统统一分配坐席",
                "external_api": "/api/customer-service/call",
            },
        ],
    )


# 新增：批量生成随机商品数据，覆盖更多类别并生成更丰富描述与图片
def seed_products(count: int, db: Session) -> List[Product]:
    categories = [
        "手机", "电脑", "家电", "服饰", "鞋靴", "美妆", "食品", "图书", "运动",
        "母婴", "家具", "汽车", "玩具", "数码", "户外", "宠物", "手表", "珠宝",
    ]

    # 名称到分类的映射，确保“商品名称”和“所属分类”一致
    noun_to_category = {
        "手机": "手机",
        "笔记本": "电脑",
        "耳机": "数码",
        "电视": "家电",
        "冰箱": "家电",
        "洗衣机": "家电",
        "连衣裙": "服饰",
        "运动鞋": "鞋靴",
        "口红": "美妆",
        "巧克力": "食品",
        "小说": "图书",
        "篮球": "运动",
        "奶粉": "母婴",
        "沙发": "家具",
        "行车记录仪": "汽车",
        "积木": "玩具",
        "相机": "数码",
        "冲锋衣": "户外",
        "猫粮": "宠物",
        "项链": "珠宝",
        "手表": "手表",
    }

    # 确保类别表存在这些类别
    for name in categories:
        exists = db.query(Category).filter(Category.name == name).first()
        if not exists:
            db.add(Category(name=name))
    db.commit()

    # 使用数据库中的分类名称，避免与硬编码列表不一致
    db_categories = [r[0] for r in db.query(Category.name).all()]
    if not db_categories:
        db_categories = categories  # 兜底，理论上不会发生

    adjectives = ["智能", "高端", "轻薄", "柔软", "运动", "专业", "便携", "舒适", "经典", "热销", "限量", "酷炫", "环保", "坚固", "安全"]
    nouns = [
        "手机", "笔记本", "耳机", "电视", "冰箱", "洗衣机", "连衣裙", "运动鞋", "口红", "巧克力", "小说", "篮球", "奶粉", "沙发", "行车记录仪", "积木", "相机", "冲锋衣", "猫粮", "项链", "手表"
    ]
    scenes = ["居家", "办公", "户外", "运动", "旅行", "学习", "娱乐", "摄影"]

    # 分类到图片关键字映射，生成与类别匹配的占位图
    category_to_slug = {
        "手机": "phone",
        "电脑": "laptop",
        "家电": "appliance",
        "服饰": "clothing",
        "鞋靴": "shoes",
        "美妆": "cosmetics",
        "食品": "food",
        "图书": "book",
        "运动": "sport",
        "母婴": "baby",
        "家具": "furniture",
        "汽车": "car",
        "玩具": "toy",
        "数码": "camera",
        "户外": "outdoor",
        "宠物": "pet",
        "手表": "watch",
        "珠宝": "jewelry",
    }

    created: List[Product] = []
    for _ in range(max(1, count)):
        noun = random.choice(nouns)
        adj = random.choice(adjectives)
        scene = random.choice(scenes)
        name = f"{adj}{noun}{random.randint(100, 999)}"
        description = (
            f"这是一款{adj}的{noun}，适合{scene}使用。\n"
            f"特点：{random.choice(['做工精细','续航持久','散热优秀','兼容性强','材质舒适','外观时尚'])}；"
            f"支持{random.choice(['极速快充','蓝牙连接','防水防尘','AI算法优化','多场景切换'])}。\n"
            f"保修：{random.choice(['一年质保','两年延保','七天无理由退换'])}。"
        )
        price = round(random.uniform(9.9, 9999.0), 2)
        stock = random.randint(0, 500)
        # 关键：根据"名称(noun)"确定所属分类
        category_name = noun_to_category.get(noun, random.choice(db_categories))
        # 先创建商品（不设置image_url），获取ID后再生成图片
        p = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category_name,
            image_url=None,  # 先不设置，等获取ID后再生成
        )
        db.add(p)
        created.append(p)
    # 提交以获取所有商品的ID
    db.commit()
    # 为每个商品生成基于ID的固定图片
    for p in created:
        db.refresh(p)
        p.image_url = _generate_image_url_from_name(p.name, p.category, p.id)
    db.commit()
    # 再次刷新以确保图片URL已保存
    for p in created:
        db.refresh(p)
    return created


# 新增：返回类别表中的分类列表（按名称）
def list_categories(db: Session) -> List[str]:
    rows = db.query(Category.name).order_by(Category.name.asc()).all()
    return [r[0] for r in rows if r and r[0]]


def get_customer_service(product_id: int, db: Session) -> schemas.CustomerServiceResponse:
    product_exists = db.query(Product.id).filter(Product.id == product_id).first()
    if not product_exists:
        raise HTTPException(status_code=404, detail="商品不存在")

    return schemas.CustomerServiceResponse(
        product_id=product_id,
        channels=[
            {
                "channel": "online_chat",
                "description": "在线客服接入接口，请由客服系统调用 /api/customer-service/chat",
                "external_api": "/api/customer-service/chat",
            },
            {
                "channel": "phone",
                "description": "电话客服，由客服系统统一分配坐席",
                "external_api": "/api/customer-service/call",
            },
        ],
    )




