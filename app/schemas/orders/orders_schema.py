from enum import Enum
from typing import Optional

from pydantic import confloat, Field, conint, validator

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