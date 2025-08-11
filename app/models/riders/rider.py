# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 15:25
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : riders.py
# @Software: PyCharm
# ==============================
# 骑手相关模型
# ==============================
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import BaseModel
from flask_login import UserMixin


class Rider(BaseModel, UserMixin):
    """骑手模型"""
    __tablename__ = 'riders'

    # 基本信息
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200))  # 头像URL
    last_login = db.Column(db.DateTime)  # 最后登录时间

    # 配送信息
    vehicle_type = db.Column(db.String(50))  # 交通工具类型
    license_plate = db.Column(db.String(20))  # 车牌号
    delivery_radius = db.Column(db.Integer)  # 最大配送距离（米）

    # 状态
    is_available = db.Column(db.Boolean, default=True)  # 是否可接单
    is_online = db.Column(db.Boolean, default=True)  # 是否在线

    # 统计信息
    completed_orders = db.Column(db.Integer, default=0)  # 完成订单数
    average_rating = db.Column(db.Float, default=0.0)  # 平均评分

    # 关系
    orders = db.relationship('Order', backref='riders', lazy=True)
    locations = db.relationship('RiderLocation', backref='riders', lazy=True)
    assignments = db.relationship('RiderAssignment', backref='riders', lazy=True)

    # 密码处理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"rider_{self.id}"

    def __repr__(self):
        return f'<Rider {self.name}>'


class RiderLocation(BaseModel):
    """骑手实时位置"""
    __tablename__ = 'rider_locations'

    # 位置信息
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # 位置精度
    speed = db.Column(db.Float)  # 移动速度（米/秒）
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 位置时间

    # 外键
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'), nullable=False)

    def __repr__(self):
        return f'<RiderLocation ({self.latitude}, {self.longitude})>'

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