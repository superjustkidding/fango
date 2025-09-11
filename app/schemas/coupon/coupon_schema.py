# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, validate

class CouponSchema(Schema):
    """Schema for creating or updating coupons"""
    code = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    coupon_type = fields.Str(required=True, validate=validate.OneOf(["percentage", "fixed"]))
    value = fields.Float(required=True)
    min_order_amount = fields.Float(required=False, missing=0.0)
    max_discount_amount = fields.Float(required=False, allow_none=True)
    valid_from = fields.DateTime(required=True, format="iso")
    valid_to = fields.DateTime(required=True, format="iso")
    usage_limit = fields.Int(required=False, allow_none=True)
    usage_count = fields.Int(dump_only=True)  # 只读字段


class CouponUpdateSchema(Schema):
    """Schema for updating coupons"""
    code = fields.Str(validate=validate.Length(min=3, max=50))
    coupon_type = fields.Str(validate=validate.OneOf(["percentage", "fixed"]))
    value = fields.Float()
    min_order_amount = fields.Float()
    max_discount_amount = fields.Float(allow_none=True)
    valid_from = fields.DateTime(required=True, format="iso")
    valid_to = fields.DateTime(required=True, format="iso")
    usage_limit = fields.Int()
