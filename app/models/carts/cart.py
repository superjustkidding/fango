# -*- coding: utf-8 -*-
# @Time    : 2025/8/20 23:33
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : cart.py
# @Software: PyCharm

# app/models/cart/cart.py
from app import db
from datetime import datetime
from app.models import BaseModel

# 购物车模型
class Cart(BaseModel):
    __tablename__ = 'carts'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # 关系
    user = db.relationship('User', backref=db.backref('carts', lazy=True))
    restaurant = db.relationship('Restaurant', backref=db.backref('carts', lazy=True))
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'total_price': self.total_price,
            'total_quantity': self.total_quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items)

    def clear(self):
        """清空购物车"""
        for item in self.items:
            db.session.delete(item)
        db.session.commit()


# 购物车商品项模型
class CartItem(BaseModel):
    __tablename__ = 'cart_items'

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # 商品ID
    product_name = db.Column(db.String(200), nullable=False)  # 商品名称
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)  # 单价

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': self.price,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @property
    def total_price(self):
        return self.quantity * self.price

