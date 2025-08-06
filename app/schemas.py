from marshmallow import Schema, fields, validate, validates, ValidationError


class RestaurantSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    address = fields.Str(validate=validate.Length(max=200))
    phone = fields.Str(validate=validate.Length(max=20))


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    price = fields.Float(required=True)
    description = fields.Str()
    restaurant_id = fields.Int(required=True)
    image_url = fields.Str(validate=validate.URL(relative=False, error="必须是有效的URL"))

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    restaurant_id = fields.Int(required=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'preparing', 'delivering', 'completed', 'cancelled']))
    total = fields.Float()
    created_at = fields.DateTime(dump_only=True)


class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    type = fields.Str(validate=validate.OneOf(['internal', 'external']))


class InternalUserSchema(UserSchema):
    restaurant_id = fields.Int(required=True)
    position = fields.Str(required=True)


class ExternalUserSchema(UserSchema):
    address = fields.Str(required=True)
    phone = fields.Str(required=True)