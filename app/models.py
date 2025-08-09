from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from extensions.sqlalchemy_plus.sqlalchemy import make_uuid

# 后期需要将models 根据业务分层


class BaseModel(db.Model):
    """所有模型的基类，包含公共字段和方法"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    deleted = db.Column(db.Boolean, default=False)

    def save(self):
        """保存对象到数据库"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """从数据库删除对象"""
        db.session.delete(self)
        db.session.commit()

class User(BaseModel):
    """用户模型（顾客）"""
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    avatar = db.Column(db.String(200))  # 头像URL

    # 关系
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)


class Rider(BaseModel):
    """骑手模型"""
    __tablename__ = 'riders'

    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    vehicle_type = db.Column(db.String(50))  # 交通工具类型
    license_plate = db.Column(db.String(20))  # 车牌号
    is_available = db.Column(db.Boolean, default=True)

    # 关系
    orders = db.relationship('Order', backref='rider', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




class Restaurant(BaseModel):
    """餐馆模型"""
    __tablename__ = 'restaurants'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    logo = db.Column(db.String(200))  # 餐馆LOGO URL
    is_active = db.Column(db.Boolean, default=True)

    # 登录凭据
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # 关系
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)
    orders = db.relationship('Order', backref='restaurant', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MenuItem(BaseModel):
    """餐馆菜单项模型"""
    __tablename__ = 'menu_items'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))  # 菜品图片URL
    is_available = db.Column(db.Boolean, default=True)

    # 外键
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # 关系
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    reviews = db.relationship('Review', backref='menu_item', lazy=True)

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'

    # 订单状态: 待付款/已付款/准备中/派送中/已完成/已取消
    uuid = db.Column(db.String(32), default=make_uuid)
    status = db.Column(db.String(20), default='pending', nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.String(200), nullable=False)
    special_instructions = db.Column(db.Text)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'))

    # 关系
    items = db.relationship('OrderItem', backref='order', lazy=True)
    review = db.relationship('Review', backref='order', uselist=False, lazy=True)

class OrderItem(BaseModel):
    """订单项模型（订单与菜单项的多对多关联）"""
    __tablename__ = 'order_items'

    quantity = db.Column(db.Integer, default=1, nullable=False)
    price_at_order = db.Column(db.Float, nullable=False)  # 下单时的价格

    # 外键
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)

class Review(BaseModel):
    """评论模型"""
    __tablename__ = 'reviews'

    rating = db.Column(db.Integer, nullable=False)  # 评分 1-5
    comment = db.Column(db.Text)
    is_for_restaurant = db.Column(db.Boolean, default=False)  # True为评价餐馆，False为评价菜品

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)




    items = db.relationship('Product', backref='product')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    items = db.relationship('OrderItem', backref='order')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

