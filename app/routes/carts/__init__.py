from app.routes.carts.resources import CartResource, CartItemResource, CartItemListResource


def register_cart_routes(api):
    api.add_resource(CartResource, '/carts/<int:user_id>')  # 用户获取所有购物车及清空
    api.add_resource(CartItemResource, '/carts/<int:user_id>/items')  # 添加商品到购物车
    api.add_resource(CartItemListResource, '/cart/<int:product_id>')  # 更新、移除商品

    return [
        'api.CartResource',
        'api.CartItemResource',
        'api.CartItemListResource'
        ]
