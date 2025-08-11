# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import re


class BaseSchema(Schema):
    """基础校验Schema"""

    class Meta:
        datetimeformat = '%Y-%m-%d %H:%M:%S'

    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(allow_none=True)
    deleted = fields.Boolean(dump_only=True)

class UserSchema(BaseSchema):
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=50),
        validate.Regexp(r'^[a-zA-Z0-9_]+$', error="只能包含字母、数字和下划线")
    ])
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=[
        validate.Length(min=8, max=128),
        validate.Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$',
                       error="必须包含大小写字母和数字")
    ])
    phone = fields.Str(validate=[
        validate.Regexp(r'^1[3-9]\d{9}$', error="必须是有效的中国手机号")
    ])
    address = fields.Str(validate=validate.Length(max=200))
    avatar = fields.Url(allow_none=True)

    @validates('username')
    def validate_username(self, value):
        if value.lower() in ['admin', 'root', 'system']:
            raise ValidationError("不允许使用保留用户名")


class RiderSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    phone = fields.Str(required=True, validate=[
        validate.Regexp(r'^1[3-9]\d{9}$')
    ])
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=[
        validate.Length(min=8, max=128)
    ])
    vehicle_type = fields.Str(validate=validate.OneOf(
        ['bicycle', 'motorcycle', 'car', 'electric_bike']
    ))
    license_plate = fields.Str(validate=[
        validate.Regexp(r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4,5}[A-Z0-9挂学警港澳]{1}$',
                       error="无效的车牌号格式")
    ])


class RestaurantSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    address = fields.Str(required=True, validate=validate.Length(max=200))
    phone = fields.Str(required=True, validate=[
        validate.Regexp(r'^(\(\d{3,4}\)|\d{3,4}-|\s)?\d{7,14}$',
                       error="无效的联系电话")
    ])
    logo = fields.Url(allow_none=True)
    is_active = fields.Boolean()
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=[
        validate.Length(min=8, max=128)
    ])

    @validates('name')
    def validate_name(self, value):
        restricted = ['官方', '平台', '管理']
        if any(word in value for word in restricted):
            raise ValidationError("名称包含受限词汇")


class MenuItemSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(validate=validate.Length(max=1000))
    price = fields.Float(required=True, validate=[
        validate.Range(min=0.01, max=9999, error="价格必须在0.01-9999范围内")
    ])
    image = fields.Url(allow_none=True)
    is_available = fields.Boolean()
    restaurant_id = fields.Int(required=True)

    @validates('price')
    def validate_price(self, value):
        if round(value, 2) != value:
            raise ValidationError("价格最多保留两位小数")


class OrderItemSchema(Schema):
    menu_item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=[
        validate.Range(min=1, max=99, error="数量必须在1-99之间")
    ])
    price_at_order = fields.Float(required=True, validate=[
        validate.Range(min=0.01)
    ])

class OrderSchema(BaseSchema):
    status = fields.Str(validate=validate.OneOf(
        ['pending', 'paid', 'preparing', 'delivering', 'completed', 'cancelled']
    ))
    total_amount = fields.Float(required=True, validate=[
        validate.Range(min=0.01)
    ])
    delivery_address = fields.Str(required=True, validate=validate.Length(max=200))
    special_instructions = fields.Str(validate=validate.Length(max=500))
    user_id = fields.Int(required=True)
    restaurant_id = fields.Int(required=True)
    rider_id = fields.Int(allow_none=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True)

    @validates('items')
    def validate_items(self, value):
        if len(value) < 1:
            raise ValidationError("订单必须包含至少一个项目")
        if len(value) > 20:
            raise ValidationError("单个订单最多包含20个项目")


class ReviewSchema(BaseSchema):
    rating = fields.Int(required=True, validate=[
        validate.Range(min=1, max=5, error="评分必须在1-5之间")
    ])
    comment = fields.Str(validate=validate.Length(max=1000))
    is_for_restaurant = fields.Boolean()
    user_id = fields.Int(required=True)
    restaurant_id = fields.Int(allow_none=True)
    menu_item_id = fields.Int(allow_none=True)
    order_id = fields.Int(required=True)

    @validates('comment')
    def validate_comment(self, value):
        if value and len(value.strip()) < 10:
            raise ValidationError("评论至少需要10个有效字符")
        banned_words = ['垃圾', '骗子', '差劲']
        if any(word in value for word in banned_words):
            raise ValidationError("评论包含不恰当词汇")