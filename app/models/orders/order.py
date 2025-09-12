# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 15:28
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : order.py
# @Software: PyCharm

# ==============================
# 业务相关模型
# ==============================
from app import db
from app.models import BaseModel
from extensions.sqlalchemy_plus.sqlalchemy import make_uuid


class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'

    # 订单状态
    STATUS_PENDING = 'pending'  # 待付款
    STATUS_PAID = 'paid'  # 已付款
    STATUS_PREPARING = 'preparing'  # 准备中
    STATUS_READY = 'ready'  # 准备完成

    STATUS_DELIVERING = 'delivering'  # 配送中
    STATUS_COMPLETED = 'completed'  # 已完成
    STATUS_CANCELED = 'canceled'  # 已取消

    # 订单信息
    uuid = db.Column(db.String(32), default=make_uuid)
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # 订单总金额
    delivery_fee = db.Column(db.Float, default=0.0)  # 配送费
    discount_amount = db.Column(db.Float, default=0.0)  # 优惠金额
    final_amount = db.Column(db.Float, nullable=False)  # 实付金额
    delivery_address = db.Column(db.String(200), nullable=False)
    special_instructions = db.Column(db.Text)  # 特殊要求
    estimated_preparation_time = db.Column(db.Integer)  # 预计准备时间（分钟）
    estimated_delivery_time = db.Column(db.DateTime)  # 预计送达时间
    actual_delivery_time = db.Column(db.DateTime)  # 实际送达时间

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))  # 使用的优惠券
    address_id = db.Column(db.Integer, db.ForeignKey('user_addresses.id'))  # 使用的地址

    # 关系
    items = db.relationship('OrderItem', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)
    review = db.relationship('Review', backref='order', uselist=False, lazy=True)
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True)
    assigned_riders = db.relationship('RiderAssignment', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'status': self.status,
            'total_amount': self.total_amount,
            'delivery_fee': self.delivery_fee,
            'discount_amount': self.discount_amount,
            'final_amount': self.final_amount,
            'delivery_address': self.delivery_address,
            'special_instructions': self.special_instructions,
            'estimated_preparation_time': self.estimated_preparation_time,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,

        }


class OrderItem(BaseModel):
    """订单项"""
    __tablename__ = 'order_items'

    # 商品信息
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price_at_order = db.Column(db.Float, nullable=False)  # 下单时的价格
    special_instructions = db.Column(db.Text)  # 单品特殊要求

    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)

    # 关系
    selected_options = db.relationship('OrderItemOption', backref='order_item', lazy=True)

    def __repr__(self):
        return f'<OrderItem {self.menu_item_id} x {self.quantity}>'


class OrderItemOption(BaseModel):
    """订单项选项"""
    __tablename__ = 'order_item_options'

    # 外键
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('menu_options.id'), nullable=False)

    # 关系
    option = db.relationship('MenuOption', backref='order_item_options', lazy=True)

    def __repr__(self):
        return f'<OrderItemOption {self.option_id}>'


class OrderStatusHistory(BaseModel):
    """订单状态历史"""
    __tablename__ = 'order_status_history'

    # 状态变更信息
    status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)  # 状态变更说明

    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    actor_id = db.Column(db.Integer)  # 操作人ID（用户、商家或骑手）
    actor_type = db.Column(db.String(20))  # 操作人类型（users, restaurant, riders）

    def __repr__(self):
        return f'<OrderStatusHistory {self.status} at {self.created_at}>'


class Review(BaseModel):
    """订单评价"""
    __tablename__ = 'reviews'

    # 评价信息
    rating = db.Column(db.Integer, nullable=False)  # 整体评分 1-5
    comment = db.Column(db.Text)
    reply = db.Column(db.Text)  # 商家回复
    reply_at = db.Column(db.DateTime)  # 回复时间
    is_anonymous = db.Column(db.Boolean, default=False)  # 是否匿名

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    # 关系
    item_reviews = db.relationship('ItemReview', backref='main_review', lazy=True)

    def __repr__(self):
        return f'<Review {self.rating} stars>'

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'reply': self.reply,
            'reply_at': self.reply_at,
            'is_anonymous': self.is_anonymous,
            'item_reviews': self.item_reviews.to_dict(),
        }

class ItemReview(BaseModel):
    """菜品评价"""
    __tablename__ = 'item_reviews'

    # 评价信息
    rating = db.Column(db.Integer, nullable=False)  # 菜品评分 1-5
    comment = db.Column(db.Text)

    # 外键
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)

    def __repr__(self):
        return f'<ItemReview for {self.menu_item_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'menu_item_id': self.menu_item_id,
        }