# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 16:03
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : coupons.py
# @Software: PyCharm

from app import db
from app.models import BaseModel


class Coupon(BaseModel):
    """优惠券"""
    __tablename__ = 'coupons'

    # 优惠券类型
    TYPE_PERCENTAGE = 'percentage'  # 百分比折扣
    TYPE_FIXED = 'fixed'  # 固定金额折扣

    # 优惠券信息
    code = db.Column(db.String(50), unique=True, nullable=False)   # 券码
    coupon_type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, nullable=False)  # 折扣值
    min_order_amount = db.Column(db.Float, default=0.0)  # 最低订单金额
    max_discount_amount = db.Column(db.Float)  # 最大折扣金额（百分比折扣时）
    valid_from = db.Column(db.DateTime, nullable=False)  # 有效期开始
    valid_to = db.Column(db.DateTime, nullable=False)  # 有效期结束
    usage_limit = db.Column(db.Integer)  # 使用次数限制
    usage_count = db.Column(db.Integer, default=0)  # 已使用次数

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # 关系
    orders = db.relationship('Order', backref='coupon', lazy=True)

    def __repr__(self):
        return f'<Coupon {self.code}>'

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "coupon_type": self.coupon_type,
            "value": self.value,
            "min_order_amount": self.min_order_amount,
            "max_discount_amount": self.max_discount_amount,
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat(),
            "usage_limit": self.usage_limit,
            "usage_count": self.usage_count,
            "restaurant_id": self.restaurant_id,
        }