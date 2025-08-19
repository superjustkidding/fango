# -*- coding: utf-8 -*-

from flask_marshmallow import Schema
from marshmallow import fields, validate


class Restaurant(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True, validate=validate.Email())
    address = fields.Str(required=True, validate=validate.Length(min=3))
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=True, validate=validate.Length(min=3))


class UpdateRestaurant(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True, validate=validate.Email())
    address = fields.Str(required=True, validate=validate.Length(min=3))
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(required=True, validate=validate.Length(min=3))
    logo = fields.Str(required=True, validate=validate.Length(min=6))


class RestaurantLoginSchema(Schema):
    email = fields.Email(required=True, error_messages={"invalid": "邮箱格式无效"})
    password_hash = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=20),
        error_messages={"required": "密码不能为空"}
    )


class MenuItem(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(max=200))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))






