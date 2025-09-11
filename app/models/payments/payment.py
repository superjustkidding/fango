# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 16:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : payment.py
# @Software: PyCharm

from app import db
from app.models import BaseModel


class Payment(BaseModel):
    """支付订单模型"""
    __tablename__ = 'payment'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 关联用户ID
    out_trade_no = db.Column(db.String(32), unique=True, nullable=False)  # 商户订单号
    transaction_id = db.Column(db.String(32))  # 微信支付订单号
    total_fee = db.Column(db.Integer, nullable=False)  # 订单金额(分)
    body = db.Column(db.String(128), nullable=False)  # 商品描述
    attach = db.Column(db.String(127))  # 附加数据
    trade_type = db.Column(db.String(16), default='JSAPI')  # 交易类型
    prepay_id = db.Column(db.String(64))  # 预支付交易会话标识
    openid = db.Column(db.String(128))  # 用户标识
    status = db.Column(db.String(16), default='NOTPAY')  # 支付状态
    bank_type = db.Column(db.String(16))  # 付款银行
    cash_fee = db.Column(db.Integer)  # 现金支付金额
    time_end = db.Column(db.String(14))  # 支付完成时间
    err_code = db.Column(db.String(32))  # 错误代码
    err_code_des = db.Column(db.String(128))  # 错误描述

    # 关联用户
    user = db.relationship('User', backref=db.backref('payment_orders', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'out_trade_no': self.out_trade_no,
            'transaction_id': self.transaction_id,
            'total_fee': self.total_fee,
            'body': self.body,
            'attach': self.attach,
            'trade_type': self.trade_type,
            'prepay_id': self.prepay_id,
            'openid': self.openid,
            'status': self.status,
            'bank_type': self.bank_type,
            'cash_fee': self.cash_fee,
            'time_end': self.time_end,
            'err_code': self.err_code,
            'err_code_des': self.err_code_des,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
