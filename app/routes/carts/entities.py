# -*- coding: utf-8 -*-
from app import db
from app.models.carts.cart import Cart, CartItem
from app.routes.logger import logger
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode


class CartEntity:
    def __init__(self, user_id):
        self.user_id = user_id
        self.cart = Cart.query.filter_by(user_id=self.user_id).first()

    # 用户获取所有购物车
    def get_user_cart(self):
        cart = Cart.query.filter_by(user_id=self.user_id).all()
        if not cart:
            cart = Cart(user_id=self.user_id)
            db.session.add(cart)
            db.session.commit()
            db.session.refresh(cart)
        return [c.to_dict() for c in cart], ECode.SUCC

    # 清空购物车
    def delete_cart(self):
        self.cart.clear()
        logger.info("Cart cleared for user_id=%s", self.user_id)
        return {'msg': 'Cart cleared'}


class CartItemEntity:
    def __init__(self, user_id):
        self.user_id = user_id
        self.cart = Cart.query.filter_by(user_id=self.user_id).first()

        if not self.cart:
            self.cart = Cart(user_id=user_id)
            db.session.add(self.cart)
            db.session.commit()
            logger.info("Created new cart user_id=%s", user_id)

    def add_item(self, product_id, quantity, price, product_name):
        """添加商品到购物车"""
        if quantity <= 0:
            raise ValueError("Quantity must be gather than 0", ECode.FORBID)

        existing_item = next((item for item in self.cart.items if item.product_id == product_id), None)

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(
                cart_id=self.cart.id,
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                price=price
                )
            db.session.add(new_item)
        db.session.commit()
        logger.info("Added new item product_id=%s", product_id)
        return self.cart.to_dict(), ECode.SUCC

class CartItemListEntity:
    def __init__(self, product_id):
        self.product_id = product_id
        self.cart_item = CartItem.query.filter_by(product_id=product_id).first()
        if not self.cart_item:
            raise BusinessValidationError("CartItem not found", ECode.FORBID)

    def update_item_quantity(self, quantity):
        """更新商品数量"""
        if quantity <= 0:
            return self.remove_item()
        self.cart_item.quantity = quantity
        db.session.commit()
        logger.info("Updated item product_id=%s ,quantity=%s", self.product_id, quantity)
        return self.cart_item.to_dict(), ECode.SUCC

    def remove_item(self):
        db.session.delete(self.cart_item)
        db.session.commit()
        logger.info("Removed product_id=%s ", self.product_id)
        return self.cart_item.to_dict(), ECode.SUCC





