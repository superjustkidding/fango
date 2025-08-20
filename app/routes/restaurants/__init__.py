# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 11:30
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import RestaurantListResource, RestaurantResource, RestaurantLoginResource,  \
    MenuCategoryResource, MenuItemResource, MenuItemListResource


def register_restaurant_routes(api):
    """注册餐厅路由到主API"""
    api.add_resource(RestaurantListResource, '/restaurants')  # 餐馆
    api.add_resource(RestaurantResource, '/restaurants/<int:restaurant_id>')  # 餐馆详情
    api.add_resource(RestaurantLoginResource, '/restaurants/login')  # 餐馆登录
    api.add_resource(MenuItemListResource, '/restaurants/<int:restaurant_id>/menu')  # 菜品
    api.add_resource(MenuItemResource, '/menuitems/<int:menuitem_id>')
    api.add_resource(MenuCategoryResource, '/restaurants/<int:restaurant_id>/menucategory')  # 菜品分类

    # 返回需要保护的端点列表
    return [
        'api.RestaurantListResource',
        'api.RestaurantResource',
        'api.RestaurantLoginResource',
        'api.MenuItemResource',
        'api.MenuItemListResource'
        'api.MenuCategoryResource',
    ]

