from datetime import datetime

from . import db

# 后期需要将models 根据业务分层

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    # 关系定义
    products = db.relationship('Product', backref='restaurant', lazy=True)
    internal_users = db.relationship('InternalUser', backref='restaurant', lazy=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20))  # 'internal' or 'external'


class InternalUser(User):
    __tablename__ = 'internal_users'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    position = db.Column(db.String(50))


class ExternalUser(User):
    __tablename__ = 'external_users'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('p_categories.id'))

    #关联餐厅
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    restaurant = db.relationship('Restaurant', backref='products', lazy=True)

class P_Category(db.Model):
    __tablename__ = 'p_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255))  # 分类图标URL
    sort_order = db.Column(db.Integer, default=0)  # 同级排序
    is_active = db.Column(db.Boolean, default=True)  # 是否启用

    # 关联餐厅
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    restaurant = db.relationship('Restaurant', backref='p_categories')

    items = db.relationship('Product', backref='product')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 关系
    items = db.relationship('OrderItem', backref='order')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)



