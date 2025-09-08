from marshmallow import Schema, fields


class CartItemSchema(Schema):
    product_id = fields.Int(required=True)
    product_name = fields.Str(required=True)
    quantity = fields.Int(required=True)
    price = fields.Float(required=True)

class UpdateCartItemSchema(Schema):
    quantity = fields.Int(required=True)