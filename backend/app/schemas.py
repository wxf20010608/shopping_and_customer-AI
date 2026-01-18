from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import (
    OrderStatusEnum,
    PaymentMethodEnum,
    ShippingStatusEnum,
)


class TimestampSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class UserRead(TimestampSchema):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class UserLogin(BaseModel):
    identity: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)


class AddressCreate(BaseModel):
    receiver_name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    detail: str
    is_default: bool = False


class AddressUpdate(BaseModel):
    receiver_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detail: Optional[str] = None
    is_default: Optional[bool] = None


class AddressRead(TimestampSchema):
    id: int
    user_id: int
    receiver_name: str
    phone: str
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    detail: str
    is_default: bool


class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    image_url: Optional[str]


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase, TimestampSchema):
    id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class ProductPage(BaseModel):
    items: List[ProductRead]
    total: int
    page: int
    page_size: int

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)

class CategoryRead(TimestampSchema):
    id: int
    name: str

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartItemRead(TimestampSchema):
    id: int
    product: ProductRead
    quantity: int


class CartRead(TimestampSchema):
    id: int
    user_id: int
    items: List[CartItemRead]


class OrderItemRead(TimestampSchema):
    id: int
    product: ProductRead
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    payment_method: PaymentMethodEnum
    shipping_carrier: str
    shipping_address: str
    tracking_number: Optional[str] = None
    use_membership: Optional[bool] = False
    coupon_id: Optional[int] = None


class OrderRead(TimestampSchema):
    id: int
    user_id: int
    status: OrderStatusEnum
    total_amount: float
    payment_method: PaymentMethodEnum
    shipping_address: str
    items: List[OrderItemRead]
    shipping: Optional["ShippingInfoRead"]
    discount_type: Optional[str] = None
    discount_amount: float = 0.0
    applied_coupon_id: Optional[int] = None
    deleted_by_user: bool = False
    deleted_at: Optional[datetime] = None


class ShippingInfoRead(TimestampSchema):
    id: int
    order_id: int
    carrier: str
    tracking_number: Optional[str]
    status: ShippingStatusEnum
    estimated_delivery: Optional[datetime]


class PaymentResult(BaseModel):
    order_id: int
    status: str
    message: str


class CustomerServiceResponse(BaseModel):
    product_id: int
    channels: List[dict]


# 会员
class MembershipCreate(BaseModel):
    level: Optional[str] = Field(default="standard", max_length=50)
    plan_id: Optional[int] = None
    extra_info: Optional[str] = None


class MembershipUpdate(BaseModel):
    level: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    plan_id: Optional[int] = None
    extra_info: Optional[str] = None


class MembershipRead(TimestampSchema):
    id: int
    user_id: int
    level: str
    plan_id: Optional[int]
    balance: float
    status: str
    extra_info: Optional[str]


class MembershipRecharge(BaseModel):
    amount: float = Field(..., gt=0)


# 优惠券
class CouponCreate(BaseModel):
    code: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    discount_type: str = Field(..., pattern="^(amount|percent)$")
    discount_value: float = Field(..., gt=0)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    min_spend: Optional[float] = 0.0
    active: bool = True
    allowed_product_id: Optional[int] = None


class CouponUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    discount_type: Optional[str] = Field(None, pattern="^(amount|percent)$")
    discount_value: Optional[float] = Field(None, gt=0)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    min_spend: Optional[float] = None
    active: Optional[bool] = None
    allowed_product_id: Optional[int] = None


class CouponRead(TimestampSchema):
    id: int
    code: str
    description: Optional[str]
    discount_type: str
    discount_value: float
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    min_spend: float
    active: bool
    allowed_product_id: Optional[int]


class UserCouponRead(TimestampSchema):
    id: int
    user_id: int
    status: str
    used_order_id: Optional[int]
    coupon: CouponRead


CartRead.model_rebuild()
OrderRead.model_rebuild()
ShippingInfoRead.model_rebuild()


# 会员计划
class MembershipPlanCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    discount_percent: float = Field(default=10, ge=0, le=100)
    active: bool = True


class MembershipPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    active: Optional[bool] = None


class MembershipPlanRead(TimestampSchema):
    id: int
    code: str
    name: str
    discount_percent: float
    active: bool


# 会员卡
class MembershipCardCreate(BaseModel):
    card_no: str = Field(..., max_length=64)
    plan_id: int
    balance: float = 0.0
    published: bool = False


class MembershipCardUpdate(BaseModel):
    user_id: Optional[int] = None
    balance: Optional[float] = None
    status: Optional[str] = None
    published: Optional[bool] = None


class MembershipCardRead(TimestampSchema):
    id: int
    card_no: str
    plan_id: int
    user_id: Optional[int]
    balance: float
    status: str
    published: bool


class ChatMessageCreate(BaseModel):
    user_id: int
    product_id: Optional[int] = None
    message: str
    model: Optional[str] = None


class ChatMessageRead(TimestampSchema):
    id: int
    user_id: int
    product_id: Optional[int]
    role: str
    content: str
    retracted: bool = False

class ChatHistoryRead(BaseModel):
    items: List[ChatMessageRead]


# ========== 知识库相关 Schemas ==========

class KnowledgeDocumentBase(BaseModel):
    title: str
    content: str
    source_type: str = "manual"  # manual, pdf, web, api, database
    source_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    active: bool = True


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass


class KnowledgeDocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    active: Optional[bool] = None


class KnowledgeDocumentRead(KnowledgeDocumentBase, TimestampSchema):
    id: int
    chunk_count: int
    document_metadata: Optional[str] = None  # JSON 格式的元数据（与模型属性名一致）
    quality_score: Optional[float] = None  # 文档质量评分
    
    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型属性读取


class KnowledgeChunkRead(TimestampSchema):
    id: int
    document_id: int
    chunk_index: int
    content: str
    chunk_metadata: Optional[str] = None  # JSON 格式的元数据（与模型属性名一致）
    vector_id: Optional[int] = None
    
    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型属性读取


class KnowledgeDocumentFromUrl(BaseModel):
    url: str
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeDocumentFromDatabase(BaseModel):
    table_name: str
    columns: Optional[List[str]] = None
    limit: int = 1000
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None

