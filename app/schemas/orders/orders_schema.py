# -*- coding: utf-8 -*-
from enum import Enum
from typing import Optional, List
from flask_marshmallow import Schema
from pydantic import BaseModel, confloat, Field, conint, validator
from datetime import datetime

from app.schemas import BaseSchema


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELED = "canceled"

class ActorType(str, Enum):
    USER = "user"
    RESTAURANT = "restaurant"
    RIDER = "rider"

class OrderSchema(BaseSchema):
    status: OrderStatus = OrderStatus.PENDING
    total_amount: confloat(gt=0) = Field(..., description="订单总金额")
    delivery_fee: confloat(ge=0) = 0.0
    discount_amount: confloat(ge=0) = 0.0
    final_amount: confloat(gt=0) = Field(..., description="实付金额")
    delivery_address: str = Field(..., max_length=200)
    special_instructions: Optional[str] = None
    estimated_preparation_time: Optional[conint(gt=0)] = Field(None, description="预计准备时间(分钟)")

    @validator('final_amount')
    def validate_amounts(cls, v, values):
        if 'total_amount' in values and 'discount_amount' in values:
            expected = values['total_amount'] - values['discount_amount']
            if abs(v - expected) > 0.01:  # 允许浮点数误差
                raise ValueError("实付金额与计算金额不符")
        return v


class OrderItemSchema(BaseSchema):
    quantity: conint(gt=0) = 1
    price_at_order: confloat(gt=0)
    special_instructions: Optional[str] = None


class OrderStatusHistoryBase(BaseSchema):
    status: OrderStatus
    note: Optional[str] = None
    actor_type: ActorType


class ReviewBase(BaseSchema):
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None
    is_anonymous: bool = False


class ItemReviewBase(BaseSchema):
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None


class OrderItemOptionSchema(BaseModel):
    option_id: int = Field(..., gt=0, description="选项ID必须大于0")


class OrderItemSchemas(BaseModel):
    menu_item_id: int = Field(..., gt=0, description="菜单项ID必须大于0")
    quantity: int = Field(..., gt=0, description="数量必须大于0")
    price_at_order: confloat(gt=0) = Field(..., description="价格必须大于0")
    special_instructions: Optional[str] = Field(None, max_length=500, description="特殊说明最多500字符")
    options: Optional[List[OrderItemOptionSchema]] = Field(None, description="选项列表")


class OrderSchemas(BaseModel):
    restaurant_id: int = Field(..., gt=0, description="餐厅ID必须大于0")
    total_amount: confloat(ge=0) = Field(..., description="总金额必须大于等于0")
    delivery_fee: confloat(ge=0) = Field(0, description="配送费必须大于等于0")
    discount_amount: confloat(ge=0) = Field(0, description="折扣金额必须大于等于0")
    final_amount: confloat(ge=0) = Field(..., description="最终金额必须大于等于0")
    delivery_address: str = Field(..., min_length=5, max_length=200, description="配送地址5-200字符")
    special_instructions: Optional[str] = Field(None, max_length=500, description="特殊说明最多500字符")
    estimated_preparation_time: Optional[int] = Field(None, ge=0, le=240, description="预计准备时间0-240分钟")
    items: List[OrderItemSchema] = Field(..., min_items=1, description="至少需要一个订单项")

    @validator('final_amount')
    def validate_final_amount(cls, v, values):
        """验证最终金额是否合理"""
        if 'total_amount' in values and 'delivery_fee' in values and 'discount_amount' in values:
            expected = values['total_amount'] + values['delivery_fee'] - values['discount_amount']
            if abs(v - expected) > 0.01:  # 允许微小浮点误差
                raise ValueError(f'最终金额计算错误，应为{expected:.2f}，实际为{v:.2f}')
        return v

    @validator('discount_amount')
    def validate_discount_amount(cls, v, values):
        """验证折扣金额不超过总金额+配送费"""
        if 'total_amount' in values and 'delivery_fee' in values:
            max_discount = values['total_amount'] + values['delivery_fee']
            if v > max_discount:
                raise ValueError(f'折扣金额不能超过订单总额+配送费({max_discount:.2f})')
        return v


class OrderUpdateSchemas(BaseModel):
    status: str = Field(..., description="订单状态")
    note: Optional[str] = Field(None, max_length=500, description="状态说明最多500字符")

    @validator('status')
    def validate_status(cls, v):
        """验证订单状态是否有效"""
        valid_statuses = ['pending', 'paid', 'preparing', 'ready',
                          'delivering', 'completed', 'canceled']
        if v not in valid_statuses:
            raise ValueError(f'无效的订单状态，必须是: {", ".join(valid_statuses)}')
        return v


class OrderAssignmentSchema(BaseModel):
    rider_id: int = Field(..., gt=0, description="骑手ID必须大于0")


# 响应模型
class OrderResponse(BaseModel):
    id: int
    uuid: str
    status: str
    total_amount: float
    delivery_fee: float
    discount_amount: float
    final_amount: float
    delivery_address: str
    special_instructions: Optional[str]
    estimated_preparation_time: Optional[int]
    estimated_delivery_time: Optional[datetime]
    actual_delivery_time: Optional[datetime]
    user_id: int
    restaurant_id: int
    rider_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price_at_order: float
    special_instructions: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class OrderWithItemsResponse(OrderResponse):
    items: List[OrderItemResponse]