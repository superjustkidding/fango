# -*- coding: utf-8 -*-

from flask_marshmallow import Schema
from marshmallow import fields, validate


class Restaurant(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(min=3))
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=True, validate=validate.Length(min=3))
    is_active = fields.Bool(required=True)


class UpdateRestaurant(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(min=3))
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=True, validate=validate.Length(min=3))
    logo = fields.Str(required=True, validate=validate.Length(min=6))


class RestaurantLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=20),
        error_messages={"required": "密码不能为空"}
    )


class MenuItemSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(max=200))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    image = fields.Str(required=True)
    preparation_time = fields.Integer()
    category_id = fields.Integer(required=True)
    is_available = fields.Bool(required=True)
    is_featured = fields.Bool(required=False)


class UpdateMenuItemSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(max=200))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    image = fields.Str(required=True)
    category_id = fields.Integer(required=True)
    is_available = fields.Bool(required=True)
    is_featured = fields.Bool(required=False)


class MenuCategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str()
    display_order = fields.Int()


class MenuOptionGroupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    is_required = fields.Bool(required=True)
    max_selections = fields.Int(required=True)
    min_selections = fields.Int(required=True)


class UpdateMenuOptionGroupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    is_required = fields.Bool(required=True)
    max_selections = fields.Int()
    min_selections = fields.Int()

class MenuOptionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))


class DeliveryZoneSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    delivery_fee = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    min_order_amount = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    delivery_time = fields.Int()


class OperatingHoursSchema(Schema):
    day_of_week = fields.Int(required=True, validate=lambda x: 0 <= x <= 6)
    open_time = fields.Time(required=True)
    close_time = fields.Time(required=True)
    is_closed = fields.Bool(missing=False)


class UpdateOperatingHoursSchema(Schema):
    day_of_week = fields.Int(validate=lambda x: 0 <= x <= 6)
    open_time = fields.Time()
    close_time = fields.Time()
    is_closed = fields.Bool()

class PromotionSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    image = fields.Str(allow_none=True, validate=validate.Length(max=200))
    start_date = fields.DateTime(required=True, format="%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime(required=True, format="%Y-%m-%d %H:%M:%S")
    is_active = fields.Bool(missing=True)

class UpdatePromotionSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    image = fields.Str(allow_none=True, validate=validate.Length(max=200))
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    is_active = fields.Bool()


