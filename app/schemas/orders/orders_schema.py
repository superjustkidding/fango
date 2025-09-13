# -*- coding: utf-8 -*-
from enum import Enum
from flask_marshmallow import Schema
from marshmallow import fields, validate, validates_schema, ValidationError


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELED = "canceled"


class ActorType(str, Enum):
    USER = "user"
    RESTAURANT = "restaurant"
    RIDER = "rider"


class OrderItemOptionSchema(Schema):
    option_id = fields.Int(required=True, validate=validate.Range(min=1), description="选项ID必须大于0")


class OrderItemSchema(Schema):
    menu_item_id = fields.Int(required=True, validate=validate.Range(min=1), description="菜单项ID必须大于0")
    quantity = fields.Int(required=True, validate=validate.Range(min=1), description="数量必须大于0")
    price_at_order = fields.Float(required=True, validate=validate.Range(min=0.01), description="价格必须大于0")
    special_instructions = fields.Str(validate=validate.Length(max=500), description="特殊说明最多500字符")
    options = fields.Nested(OrderItemOptionSchema, many=True, description="选项列表")


class OrderSchema(Schema):
    restaurant_id = fields.Int(required=True, validate=validate.Range(min=1), description="餐厅ID必须大于0")
    total_amount = fields.Float(required=True, validate=validate.Range(min=0), description="总金额必须大于等于0")
    delivery_fee = fields.Float(validate=validate.Range(min=0), missing=0, description="配送费必须大于等于0")
    discount_amount = fields.Float(validate=validate.Range(min=0), missing=0, description="折扣金额必须大于等于0")
    final_amount = fields.Float(required=True, validate=validate.Range(min=0), description="最终金额必须大于等于0")
    delivery_address = fields.Str(required=True, validate=validate.Length(min=5, max=200),
                                  description="配送地址5-200字符")
    special_instructions = fields.Str(validate=validate.Length(max=500), description="特殊说明最多500字符")
    estimated_preparation_time = fields.Int(validate=validate.Range(min=0, max=240),
                                            description="预计准备时间0-240分钟")
    items = fields.Nested(OrderItemSchema, many=True, required=True, validate=validate.Length(min=1),
                          description="至少需要一个订单项")

    @validates_schema
    def validate_final_amount(self, data, **kwargs):
        """验证最终金额是否合理"""
        total = data.get('total_amount', 0)
        delivery_fee = data.get('delivery_fee', 0)
        discount = data.get('discount_amount', 0)
        final = data.get('final_amount', 0)

        expected = total + delivery_fee - discount
        if abs(final - expected) > 0.01:  # 允许微小浮点误差
            raise ValidationError(f'最终金额计算错误，应为{expected:.2f}，实际为{final:.2f}', 'final_amount')

    @validates_schema
    def validate_discount_amount(self, data, **kwargs):
        """验证折扣金额不超过总金额+配送费"""
        total = data.get('total_amount', 0)
        delivery_fee = data.get('delivery_fee', 0)
        discount = data.get('discount_amount', 0)

        max_discount = total + delivery_fee
        if discount > max_discount:
            raise ValidationError(f'折扣金额不能超过订单总额+配送费({max_discount:.2f})', 'discount_amount')


class OrderUpdateSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf([
                        'pending', 'paid', 'preparing', 'ready',
                        'delivering', 'completed', 'canceled'
                            ]), description="订单状态")
    note = fields.Str(validate=validate.Length(max=500), description="状态说明最多500字符")


class OrderAssignmentSchema(Schema):
    rider_id = fields.Int(required=True, validate=validate.Range(min=1), description="骑手ID必须大于0")


class OrderItemResponse(Schema):
    id = fields.Int()
    order_id = fields.Int()
    menu_item_id = fields.Int()
    quantity = fields.Int()
    price_at_order = fields.Float()
    special_instructions = fields.Str()
    created_at = fields.DateTime()


# 评价相关Schema
class ItemReviewSchema(Schema):
    menu_item_id = fields.Int(required=True, validate=validate.Range(min=1))
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str()


class ReviewSchema(Schema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str()
    is_anonymous = fields.Bool(missing=False)
    item_reviews = fields.Nested(ItemReviewSchema, many=True, required=False)





class ReviewRestaurantSchema(Schema):
    reply = fields.Str()


class OrderStatusHistorySchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf([s.value for s in OrderStatus]))
    note = fields.Str()
    actor_type = fields.Str(required=True, validate=validate.OneOf([a.value for a in ActorType]))