# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 16:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : payment.py
# @Software: PyCharm

from app import db
from app.models import BaseModel


class Payment(BaseModel):
    """支付记录"""
    __tablename__ = 'payments'

    # 支付状态
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'  #已退款

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

