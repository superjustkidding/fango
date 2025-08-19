# -*- coding: utf-8 -*-
# @Time    : 2025/8/9 15:12
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : restaurants.py
# @Software: PyCharm


# ==============================
# 餐厅相关模型
# ==============================

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import BaseModel
from flask_login import UserMixin

class Restaurant(BaseModel, UserMixin):
    """餐馆模型"""
    __tablename__ = 'restaurants'

    # 基本信息
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    logo = db.Column(db.String(200))  # 餐馆LOGO URL
    banner = db.Column(db.String(200))  # 餐馆横幅URL
    rating = db.Column(db.Float, default=0.0)  # 平均评分

    # 状态
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    is_online = db.Column(db.Boolean, default=True)  # 是否在线（营业）

    # 账户信息
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # 关系
    menu_categories = db.relationship('MenuCategory', backref='restaurant', lazy=True)
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)
    orders = db.relationship('Order', backref='restaurant', lazy=True)
    reviews = db.relationship('Review', backref='restaurant', lazy=True)
    delivery_zones = db.relationship('DeliveryZone', backref='restaurant', lazy=True)
    operating_hours = db.relationship('OperatingHours', backref='restaurant', lazy=True)
    promotions = db.relationship('Promotion', backref='restaurant', lazy=True)
    coupons = db.relationship('Coupon', backref='restaurant', lazy=True)

    # 密码处理
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"restaurant_{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "is_active": self.is_active,
        }

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class MenuCategory(BaseModel):
    """菜单分类"""
    __tablename__ = 'menu_categories'

    # 分类信息
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)  # 显示顺序

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # 关系
    items = db.relationship('MenuItem', backref='category', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self):
        return f'<MenuCategory {self.name}>'


class MenuItem(BaseModel):
    """菜品项"""
    __tablename__ = 'menu_items'

    # 菜品信息
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))  # 菜品图片URL
    preparation_time = db.Column(db.Integer)  # 准备时间（分钟）

    # 状态
    is_available = db.Column(db.Boolean, default=True)  # 是否可用
    is_featured = db.Column(db.Boolean, default=False)  # 是否推荐

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'))

    # 关系
    option_groups = db.relationship('MenuOptionGroup', backref='menu_item', lazy=True)
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    reviews = db.relationship('ItemReview', backref='menu_item', lazy=True)

    def to_dict(self):
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category_id" : self.category_id,
        }

    def __repr__(self):
        return f'<MenuItem {self.name}>'


class MenuOptionGroup(BaseModel):
    """菜品选项组（如加料、口味等）"""
    __tablename__ = 'menu_option_groups'

    # 选项组信息
    name = db.Column(db.String(50), nullable=False)
    is_required = db.Column(db.Boolean, default=False)  # 是否必选
    min_selections = db.Column(db.Integer, default=1)  # 最少选择数
    max_selections = db.Column(db.Integer, default=1)  # 最多选择数

    # 外键
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)

    # 关系
    options = db.relationship('MenuOption', backref='option_group', lazy=True)

    def __repr__(self):
        return f'<MenuOptionGroup {self.name}>'


class MenuOption(BaseModel):
    """菜品选项"""
    __tablename__ = 'menu_options'

    # 选项信息
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, default=0.0)  # 选项额外价格

    # 外键
    option_group_id = db.Column(db.Integer, db.ForeignKey('menu_option_groups.id'), nullable=False)

    def __repr__(self):
        return f'<MenuOption {self.name}>'


class DeliveryZone(BaseModel):
    """配送区域"""
    __tablename__ = 'delivery_zones'

    # 区域信息
    name = db.Column(db.String(50), nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)  # 配送费
    min_order_amount = db.Column(db.Float, default=0.0)  # 最低起送金额
    delivery_time = db.Column(db.Integer)  # 预计配送时间（分钟）

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # 关系
    polygons = db.relationship('DeliveryPolygon', backref='delivery_zone', lazy=True)

    def __repr__(self):
        return f'<DeliveryZone {self.name}>'


class DeliveryPolygon(BaseModel):
    """配送区域多边形坐标"""
    __tablename__ = 'delivery_polygons'

    # 坐标信息
    coordinates = db.Column(db.Text, nullable=False)  # JSON格式坐标点

    # 外键
    zone_id = db.Column(db.Integer, db.ForeignKey('delivery_zones.id'), nullable=False)

    def __repr__(self):
        return f'<DeliveryPolygon for zone {self.zone_id}>'


class OperatingHours(BaseModel):
    """营业时间"""
    __tablename__ = 'operating_hours'

    # 时间信息
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=周日, 1=周一, ..., 6=周六
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)  # 是否全天休息

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def __repr__(self):
        return f'<OperatingHours for day {self.day_of_week}>'


class Promotion(BaseModel):
    """促销活动"""
    __tablename__ = 'promotions'

    # 活动信息
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    # 状态
    is_active = db.Column(db.Boolean, default=True)

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def __repr__(self):
        return f'<Promotion {self.title}>'

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
