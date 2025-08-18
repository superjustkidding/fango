from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, confloat, validator

from app.schemas import BaseSchema

class CouponType(str, Enum):
    PERCENTAGE = "percentage"  # 百分比折扣
    FIXED = "fixed"           # 固定金额折扣

class CouponSchema(BaseSchema):
    code: str = Field(
        ...,
        min_length=6,
        max_length=50,
        example="SUMMER2023",
        description="优惠码(需大写字母和数字组合)"
    )
    coupon_type: CouponType = Field(
        ...,
        example="percentage",
        description="优惠类型: percentage/fixed"
    )
    value: confloat(gt=0) = Field(
        ...,
        example=10.0,
        description="折扣值(百分比或固定金额)"
    )
    min_order_amount: confloat(ge=0) = Field(
        default=0.0,
        example=100.0,
        description="最低订单金额"
    )
    max_discount_amount: Optional[confloat(gt=0)] = Field(
        None,
        example=50.0,
        description="最大折扣金额(仅百分比类型需要)"
    )
    valid_from: datetime = Field(
        ...,
        example="2023-08-01T00:00:00",
        description="生效时间"
    )
    valid_to: datetime = Field(
        ...,
        example="2023-08-31T23:59:59",
        description="过期时间"
    )
    usage_limit: Optional[int] = Field(
        None,
        gt=0,
        example=100,
        description="使用次数限制"
    )

    @validator('code')
    def validate_code_format(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("优惠码必须包含大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("优惠码必须包含数字")
        return v.upper()  # 统一转为大写

    @validator('valid_to')
    def validate_valid_period(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError("过期时间必须晚于生效时间")
        return v

    @validator('max_discount_amount')
    def validate_max_amount(cls, v, values):
        if values.get('coupon_type') == CouponType.PERCENTAGE and v is None:
            raise ValueError("百分比折扣必须设置最大折扣金额")
        if values.get('coupon_type') == CouponType.FIXED and v is not None:
            raise ValueError("固定折扣不应设置最大折扣金额")
        return v