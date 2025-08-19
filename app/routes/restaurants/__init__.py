# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 11:30
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import RestaurantListResource, RestaurantResource, RestaurantLoginResource, MenuItemResource, \
    MenuCategoryResource


def register_restaurant_routes(api):
    """注册餐厅路由到主API"""
    api.add_resource(RestaurantListResource, '/restaurants')
    api.add_resource(RestaurantResource, '/restaurants/<int:restaurant_id>')
    api.add_resource(RestaurantLoginResource, '/restaurants/login')
    api.add_resource(MenuItemResource, '/restaurants/<int:restaurant_id>/menu')
    api.add_resource(MenuCategoryResource, '/restaurants/<int:restaurant_id>/menucategory')


    # 返回需要保护的端点列表
    return [
        'api.RestaurantListResource',
        'api.RestaurantResource',
        'api.RestaurantLoginResource',
        'api.MenuItemResource',
    ]

