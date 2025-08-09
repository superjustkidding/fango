# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 15:28
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : orders.py
# @Software: PyCharm

# ==============================
# 业务相关模型
# ==============================
from app import db
from datetime import datetime
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
    actor_type = db.Column(db.String(20))  # 操作人类型（user, restaurant, rider）

    def __repr__(self):
        return f'<OrderStatusHistory {self.status} at {self.created_at}>'


class Payment(BaseModel):
    """支付记录"""
    __tablename__ = 'payments'

    # 支付状态
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    # 支付信息
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # wechat, alipay, card, cash
    transaction_id = db.Column(db.String(100))  # 第三方支付ID
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    paid_at = db.Column(db.DateTime)  # 支付时间

    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    def __repr__(self):
        return f'<Payment {self.amount} via {self.payment_method}>'


class Coupon(BaseModel):
    """优惠券"""
    __tablename__ = 'coupons'

    # 优惠券类型
    TYPE_PERCENTAGE = 'percentage'  # 百分比折扣
    TYPE_FIXED = 'fixed'  # 固定金额折扣

    # 优惠券信息
    code = db.Column(db.String(50), unique=True, nullable=False)
    coupon_type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, nullable=False)  # 折扣值
    min_order_amount = db.Column(db.Float, default=0.0)  # 最低订单金额
    max_discount_amount = db.Column(db.Float)  # 最大折扣金额（百分比折扣时）
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer)  # 使用次数限制
    usage_count = db.Column(db.Integer, default=0)  # 已使用次数

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # 关系
    orders = db.relationship('Order', backref='coupon', lazy=True)

    def __repr__(self):
        return f'<Coupon {self.code}>'


class RiderAssignment(BaseModel):
    """骑手订单分配"""
    __tablename__ = 'rider_assignments'

    # 分配状态
    STATUS_PENDING = 'pending'  # 待接受
    STATUS_ACCEPTED = 'accepted'  # 已接受
    STATUS_REJECTED = 'rejected'  # 已拒绝
    STATUS_CANCELED = 'canceled'  # 已取消

    # 分配信息
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)  # 分配时间
    responded_at = db.Column(db.DateTime)  # 响应时间

    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'), nullable=False)

    def __repr__(self):
        return f'<RiderAssignment {self.order_id} to {self.rider_id}>'


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


class RestaurantStatistics(BaseModel):
    """餐馆统计数据"""
    __tablename__ = 'restaurant_statistics'

    # 统计信息
    date = db.Column(db.Date, nullable=False)
    total_orders = db.Column(db.Integer, default=0)
    completed_orders = db.Column(db.Integer, default=0)
    canceled_orders = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    average_rating = db.Column(db.Float, default=0.0)
    popular_items = db.Column(db.Text)  # JSON格式热门菜品

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def __repr__(self):
        return f'<RestaurantStats {self.date}>'
