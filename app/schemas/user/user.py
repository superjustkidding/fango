from marshmallow import Schema, fields, validate, validates, ValidationError

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
