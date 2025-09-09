from flask import request
from flask_restful import Resource

from app.routes.carts.entities import CartEntity, CartItemEntity, CartItemListEntity
from app.routes.jwt import current_user, user_required
from app.schemas.carts.cart_schema import CartItemSchema, UpdateCartItemSchema
from app.utils.validation import validate_request


class CartResource(Resource):
    endpoint = 'api.CartResource'

    @user_required
    def get(self, user_id, restaurant_id):
        entity = CartEntity(
            current_user=current_user,
            user_id=user_id,
            restaurant_id=restaurant_id)
        return entity.get_user_cart()

    @user_required
    def delete(self, user_id, restaurant_id):
        entity = CartEntity(
            current_user=current_user,
            user_id=user_id,
            restaurant_id=restaurant_id
        )
        return entity.delete_cart()

class CartItemResource(Resource):
    endpoint = 'api.CartItemResource'

    """添加商品到购物车"""

    @user_required
    def post(self, user_id, restaurant_id):
        data = validate_request(CartItemSchema, request.get_json())
        entity = CartItemEntity(
            user_id=user_id,
            restaurant_id=restaurant_id,
        )
        return entity.add_item(
            product_id=data["product_id"],
            quantity=data["quantity"],
           )


class CartItemListResource(Resource):
    endpoint = 'api.CartItemListResource'

    @user_required
    def put(self, restaurant_id, product_id):
        data = validate_request(UpdateCartItemSchema, request.get_json())
        entity = CartItemListEntity(
            restaurant_id=restaurant_id,
            product_id=product_id
        )
        return entity.update_item_quantity(quantity=data["quantity"])

    @user_required
    def delete(self, restaurant_id, product_id):
        entity = CartItemListEntity(
            restaurant_id=restaurant_id,
            product_id=product_id
        )
        return entity.remove_item()

