# -*- coding: utf-8 -*-

from enum import Enum
from pydantic import validator, Field, confloat
from app.schemas import BaseSchema
from marshmallow import Schema, fields, validate

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


class WeChatPayCreateOrderSchema(Schema):
    """微信支付创建订单参数验证"""
    total_fee = fields.Integer(required=True, validate=validate.Range(min=1))  # 金额(分)
    body = fields.String(required=True, validate=validate.Length(max=128))  # 商品描述
    attach = fields.String(validate=validate.Length(max=127))  # 附加数据
    trade_type = fields.String(validate=validate.OneOf(['JSAPI', 'NATIVE', 'APP']))  # 交易类型
    openid = fields.String(validate=validate.Length(max=128))  # 用户标识(JSAPI必传)
    out_trade_no = fields.String(validate=validate.Length(max=32))  # 商户订单号
    spbill_create_ip = fields.String(validate=validate.Length(max=16))  # 终端IP

