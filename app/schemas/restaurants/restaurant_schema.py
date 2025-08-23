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
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    is_required = fields.Bool(required=True)
    max_selections = fields.Int()
    min_selections = fields.Int()

class MenuOptionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))







