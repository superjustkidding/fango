# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 11:30
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import RestaurantListResource, RestaurantResource, RestaurantLoginResource, \
    MenuCategoryResource, MenuItemResource, MenuItemListResource, MenuCategoryListResource, MenuOptionGroupListResource, \
    MenuOptionGroupResource, MenuOptionListResource, MenuOptionResource, DeliveryZoneListResource, DeliveryZoneResource, \
    OperatingHoursListResource, OperatingHoursResource, PromotionListResource, PromotionResource, \
    DeliveryPolygonListResource, DeliveryPolygonResource, RestaurantStatisticsResource, RestaurantStatisticsListResource


def register_restaurant_routes(api):
    """注册餐厅路由到主API"""
    api.add_resource(RestaurantListResource, '/restaurants')  # 餐馆
    api.add_resource(RestaurantResource, '/restaurants/<int:restaurant_id>')  # 餐馆详情
    api.add_resource(RestaurantLoginResource, '/restaurants/login')  # 餐馆登录
    api.add_resource(MenuItemListResource, '/restaurants/<int:restaurant_id>/menu')  # 菜品
    api.add_resource(MenuItemResource, '/menuitem/<int:menuitem_id>')  # 菜品详情
    api.add_resource(MenuCategoryListResource, '/restaurants/<int:restaurant_id>/menu_category')  # 菜品分类
    api.add_resource(MenuCategoryResource, '/categories/<int:menu_category_id>')  # 菜品分类详情
    api.add_resource(MenuOptionGroupListResource, '/menuitem/<int:menuitem_id>/option_group')  # 菜品选项组
    api.add_resource(MenuOptionGroupResource, '/option_group/<group_id>')  # 菜品选项组详情
    api.add_resource(MenuOptionListResource, '/option_group/<group_id>/options')  # 菜品选项
    api.add_resource(MenuOptionResource, '/options/<int:menu_option_id>')  # 菜品选项详情
    api.add_resource(DeliveryZoneListResource, '/restaurants/<int:restaurant_id>/delivery_zone')  # 配送区域
    api.add_resource(DeliveryZoneResource, '/delivery_zone/<int:delivery_zone_id>')  # 配送区域详情
    api.add_resource(DeliveryPolygonListResource,'/zones/<int:zone_id>/polygons')  # 配送区域多边形
    api.add_resource(DeliveryPolygonResource, "/polygons/<int:polygon_id>")  # 配送区域多边形详情
    api.add_resource(OperatingHoursListResource, '/restaurants/<int:restaurant_id>/operating_hours')  # 营业时间
    api.add_resource(OperatingHoursResource, '/operating_hours/<int:operating_hours_id>')  # 营业时间详情
    api.add_resource(PromotionListResource, '/restaurants/<int:restaurant_id>/promotion')  # 促销活动
    api.add_resource(PromotionResource, '/promotion/<int:promotion_id>')
    api.add_resource(RestaurantStatisticsResource, "/restaurants/<int:restaurant_id>/statistics")  # 日期获取统计信息
    api.add_resource(RestaurantStatisticsListResource, "/restaurants/<int:restaurant_id>/statistics/history")  # 历史统计信息

    # 返回需要保护的端点列表
    return [
        'api.RestaurantListResource',
        'api.RestaurantResource',
        'api.RestaurantLoginResource',
        'api.MenuItemResource',
        'api.MenuItemListResource',
        'api.MenuCategoryListResource',
        'api.MenuCategoryResource',
        'api.MenuOptionGroupListResource',
        'api.MenuOptionGroupResource',
        'api.DeliveryZoneListResource',
        'api.DeliveryZoneResource',
        'api.DeliveryPolygonListResource',
        'api.DeliveryPolygonResource',
        'api.OperatingHoursListResource',
        'api.OperatingHoursResource',
        'api.PromotionListResource',
        'api.PromotionResource'
    ]
