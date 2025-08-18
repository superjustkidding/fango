from enum import Enum

from pydantic import validator, Field, confloat

from app.schemas import BaseSchema

class PaymentStatus(str, Enum):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

class PaymentMethod(str, Enum):
    WECHAT = "wechat"
    ALIPAY = "alipay"
    CARD = "card"
    CASH = "cash"
    OTHER = "other"


class PaymentSchema(BaseSchema):
    amount: confloat(gt=0) = Field(
        ...,
        example=99.99,
        description="支付金额(必须大于0)"
    )
    payment_method: PaymentMethod = Field(
        ...,
        example="wechat",
        description="支付方式"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="支付状态"
    )

    @validator('amount')
    def round_amount(cls, v):
        return round(v, 2)  # 强制保留2位小数


