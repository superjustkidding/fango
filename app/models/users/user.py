# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 13:55
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : users.py
# @Software: PyCharm
# ==============================
# 用户相关模型
# ==============================

from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import BaseModel
from flask_login import UserMixin

class User(BaseModel, UserMixin):
    """用户模型（顾客）"""
    __tablename__ = 'users'

    # 基本信息
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    avatar = db.Column(db.String(200))  # 头像URL
    last_login = db.Column(db.DateTime)  # 最后登录时间
    is_admin = db.Column(db.Boolean, default=False)

    # 关系
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    user_addresses = db.relationship('UserAddress', backref='users', lazy=True)
    user_coupons = db.relationship('UserCoupon', backref='users', lazy=True)

    # 密码处理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"user_{self.id}"

    def __repr__(self):
        return f'<User {self.username}>'


class UserAddress(BaseModel):
    """用户收货地址"""
    __tablename__ = 'user_addresses'

    # 地址信息
    label = db.Column(db.String(50))  # 地址标签（家、公司等）
    recipient = db.Column(db.String(50), nullable=False)  # 收件人姓名
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(200))  # 详细地址（门牌号等）
    is_default = db.Column(db.Boolean, default=False)  # 是否默认地址

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<UserAddress {self.label} for {self.user_id}>'


class UserCoupon(BaseModel):
    """用户拥有的优惠券"""
    __tablename__ = 'user_coupons'

    # 状态
    STATUS_UNUSED = 'unused'
    STATUS_USED = 'used'
    STATUS_EXPIRED = 'expired'

    status = db.Column(db.String(20), default=STATUS_UNUSED)
    used_at = db.Column(db.DateTime)  # 使用时间

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)

    # 关系
    coupon = db.relationship('Coupon', backref='user_coupons', lazy=True)

    def __repr__(self):
        return f'<UserCoupon {self.coupon_id} for {self.user_id}>'
