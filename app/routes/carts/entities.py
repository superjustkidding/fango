from app import db
from app.models.carts.cart import Cart, CartItem
from app.routes.logger import logger
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode


class CartEntity:
    def __init__(self, current_user, user_id, restaurant_id):
        self.current_user = current_user
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.cart = Cart.query.filter_by(user_id=self.user_id, restaurant_id=self.restaurant_id).first()
        if not self.cart:
            logger.warning("Cart not found for user_id=%s", self.user_id)
            raise BusinessValidationError("Cart not found", ECode.NOTFOUND)

    # 用户获取所有购物车
    def get_user_cart(self):
        if not self.current_user:
            logger.warning("Current user not found while fetching cart, user_id=%s", self.user_id)
            raise BusinessValidationError("User not found", ECode.NOTFOUND)
        if self.current_user.id != self.user_id:
            logger.warning("User does not belong to current user", self.current_user.id, self.cart.id)
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        cart = Cart.query.filter_by(user_id=self.user_id).all()
        return [c.to_dict() for c in cart], ECode.SUCC

    # 清空购物车
    def delete_cart(self):
        self.cart.clear()
        logger.info("Cart cleared for user_id=%s", self.user_id)
        return {'msg': 'Cart cleared'}


class CartItemEntity:
    def __init__(self, user_id, restaurant_id):
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.cart = Cart.query.filter_by(user_id=self.user_id, restaurant_id=self.restaurant_id).first()

        if not self.cart:
            self.cart = Cart(user_id=user_id, restaurant_id=restaurant_id)
            db.session.add(self.cart)
            db.session.commit()

    def add_item(self, product_id, quantity, price, product_name):
        """添加商品到购物车"""
        if quantity <= 0:
            raise ValueError("Quantity must be gather than 0", ECode.FORBID)
        if self.user_id != self.cart.user_id:
            logger.warning("User does not belong to cart, user_id=%s", self.user_id)
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        existing_item = next((item for item in self.cart.items if item.product_id == product_id), None)

        if existing_item:
            existing_item.quantity += quantity
            existing_item.price = price  # 更新价格
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
    def __init__(self, restaurant_id, product_id):
        self.restaurant_id = restaurant_id
        self.product_id = product_id
        self.cart = Cart.query.filter_by(restaurant_id=self.restaurant_id).first()

    def update_item_quantity(self, quantity):
        """更新商品数量"""
        item = next((item for item in self.cart.items if item.product_id == self.product_id), None)

        if not item:
            logger.warning("Item not found for product_id=%s", self.product_id)
            raise BusinessValidationError("Item not found", ECode.NOTFOUND)

        if quantity <= 0:
            logger.info("Quantity <= 0 removing product_id=%s from cart_id=%s", self.product_id, self.cart.id)
            return self.remove_item(self.product_id), ECode.SUCC

        item.quantity = quantity
        item.price = item.price * quantity
        db.session.commit()
        return self.cart.to_dict(), ECode.SUCC

    def remove_item(self):
        item = next((item for item in self.cart.items if item.product_id == self.product_id), None)
        if item:
            db.session.delete(item)
            db.session.commit()
        else:
            raise BusinessValidationError("Item not found", ECode.NOTFOUND)
        logger.info("Removed item product_id=%s from cart_id=%s", self.product_id, self.cart.id)
        return {'msg':'removed successfully'}, ECode.SUCC





