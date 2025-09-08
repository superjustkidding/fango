# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:08
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm
from .carts import register_cart_routes
from .orders import register_order_routes
from .riders import register_rider_routes
from .users import register_user_routes
from .restaurants import register_restaurant_routes
from .uploadfiles import register_upload_routes


def register_all_routes(api, all_protected_endpoints):
    """统一注册所有子路由，并返回受保护端点"""
    # 用户路由
    user_protected = register_user_routes(api)
    all_protected_endpoints.extend(user_protected)

    # 餐厅路由
    restaurant_protected = register_restaurant_routes(api)
    all_protected_endpoints.extend(restaurant_protected)

    # 文件上传
    upload_protected = register_upload_routes(api)
    all_protected_endpoints.extend(upload_protected)

    # 骑手路由
    rider_protected = register_rider_routes(api)
    all_protected_endpoints.extend(rider_protected)

    # 订单路由
    order_protected = register_order_routes(api)
    all_protected_endpoints.extend(order_protected)

    # 购物车路由
    cart_protected = register_cart_routes(api)
    all_protected_endpoints.extend(cart_protected)

    return all_protected_endpoints
