# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, validate, validates, ValidationError


class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(validate=validate.Length(min=10, max=15))
    is_admin = fields.Boolean()

class UserCreateSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    phone = fields.Str(validate=validate.Length(min=10, max=15))
    is_admin = fields.Boolean()

class UserUpdateSchema(Schema):
    username = fields.Str(validate=validate.Length(min=3, max=80))
    email = fields.Email()
    password = fields.Str(validate=validate.Length(min=6))
    phone = fields.Str(validate=validate.Length(min=10, max=15))
    is_admin = fields.Boolean()

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserAddressSchema(Schema):
    label = fields.Str(validate=validate.Length(min=1, max=80))
    recipient = fields.Str(validate=validate.Length(min=0, max=15))
    phone = fields.Str(validate=validate.Length(min=10, max=15))
    address = fields.Str(validate=validate.Length(min=2, max=30))
    details = fields.Str(validate=validate.Length(min=2, max=30))
    is_default = fields.Boolean()