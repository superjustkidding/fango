# -*- coding: utf-8 -*-
from flask import request

from flask_restful import Resource
from app.routes.restaurants.entities import RestaurantEntity, RestaurantItemEntity, MenuItemListEntity, \
    MenuCategoryEntity, MenuItemEntity, MenuCategoryListEntity, MenuOptionGroupListEntity, MenuOptionGroupEntity, \
    MenuOptionListEntity, MenuOptionEntity, DeliveryZoneListEntity, DeliveryZoneEntity, OperatingHoursListEntity, \
    OperatingHoursEntity, PromotionListEntity, PromotionEntity, DeliveryPolygonListEntity, DeliveryPolygonEntity, \
    RestaurantStatisticsEntity
from app.schemas.restaurants.restaurant_schema import Restaurant, RestaurantLoginSchema, UpdateRestaurant, \
    MenuCategorySchema, UpdateMenuItemSchema, MenuItemSchema, MenuOptionGroupSchema, UpdateMenuOptionGroupSchema, \
    MenuOptionSchema, DeliveryZoneSchema, OperatingHoursSchema, UpdateOperatingHoursSchema, PromotionSchema, \
    UpdatePromotionSchema, DeliveryPolygonCreateSchema
from app.utils.validation import validate_request
from app.routes.jwt import current_user, restaurant_required, admin_required


class RestaurantListResource(Resource):
    endpoint = 'api.RestaurantListResource'

    @restaurant_required
    def get(self):
        entity = RestaurantEntity(current_user=current_user)
        return entity.get_restaurants(**request.args)

    def post(self):
        data = validate_request(Restaurant, request.get_json())
        entity = RestaurantEntity(current_user=current_user)
        return entity.create_restaurant(data)


class RestaurantResource(Resource):
    endpoint = 'api.RestaurantResource'

    @restaurant_required
    def get(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_restaurant()

    @restaurant_required
    def put(self, restaurant_id):
        data = validate_request(UpdateRestaurant, request.get_json())
        entity = RestaurantItemEntity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id=restaurant_id
        )
        return entity.update_restaurant(data)

    @restaurant_required
    def delete(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.delete_restaurant()


class RestaurantLoginResource(Resource):
    endpoint = 'api.RestaurantLoginResource'

    def post(self):
        data = validate_request(RestaurantLoginSchema, request.get_json())
        entity = RestaurantEntity()
        return entity.Rlogin(data)


class MenuItemListResource(Resource):
    endpoint = 'api.MenuListItemResource'

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(MenuItemSchema, request.get_json())
        entity = MenuItemListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_menuitem(data)

    @restaurant_required
    def get(self, restaurant_id):
        entity = MenuItemListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_all_menuitem()

class MenuItemResource(Resource):
    endpoint = 'api.MenuItemResource'

    @restaurant_required
    def get(self, menuitem_id):
        """获取单个菜品"""
        entity = MenuItemEntity(
            current_user=current_user,
            menuitem_id=menuitem_id
        )
        return entity.get_menuitem()

    @restaurant_required
    def put(self, menuitem_id):
        """更新单个菜品"""
        data = validate_request(UpdateMenuItemSchema, request.get_json())
        entity = MenuItemEntity(
            current_user=current_user,
            menuitem_id=menuitem_id
        )
        return entity.update_menuitem(data)

    @restaurant_required
    def delete(self, menuitem_id):
        """删除单个菜品"""
        entity = MenuItemEntity(
            current_user=current_user,
            menuitem_id=menuitem_id
        )
        return entity.delete_menuitem()


class MenuCategoryListResource(Resource):
    endpoint = 'api.MenuCategoryListResource'

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_menu_category(data)

    @restaurant_required
    def get(self, restaurant_id):
        entity = MenuCategoryListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id)
        return entity.get_menu_category(restaurant_id)


class MenuCategoryResource(Resource):
    endpoint = 'api.MenuCategoryResource'

    @restaurant_required
    def put(self, menu_category_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryEntity(
            current_user=current_user,
            menucategory_id=menu_category_id
        )
        return entity.update_menu_category(data)

    @restaurant_required
    def delete(self, menu_category_id):
        entity = MenuCategoryEntity(
            current_user=current_user,
            menucategory_id=menu_category_id
        )
        return entity.delete_menu_category()


class MenuOptionGroupListResource(Resource):
    endpoint = 'api.MenuOptionGroupListResource'

    @restaurant_required
    def get(self, menuitem_id):
        entity = MenuOptionGroupListEntity(
            current_user=current_user,
            menu_item_id=menuitem_id
        )
        return entity.get_menu_group

    @restaurant_required
    def post(self, menuitem_id):
        data = validate_request(MenuOptionGroupSchema, request.get_json())
        entity = MenuOptionGroupListEntity(
            current_user=current_user,
            menu_item_id=menuitem_id
        )
        return entity.create_menu_group(data)


class MenuOptionGroupResource(Resource):
    endpoint = 'api.MenuOptionGroupResource'

    @restaurant_required
    def put(self, group_id):
        data = validate_request(UpdateMenuOptionGroupSchema, request.get_json())
        entity = MenuOptionGroupEntity(
            current_user=current_user,
            group_id=group_id,
        )
        return entity.update_menu_group(data)

    @restaurant_required
    def delete(self, group_id):
        entity = MenuOptionGroupEntity(
            current_user=current_user,
            group_id=group_id,
        )
        return entity.delete_menu_group()


class MenuOptionListResource(Resource):
    endpoint = 'api.MenuOptionResource'

    @restaurant_required
    def get(self, group_id):
        entity = MenuOptionListEntity(
            current_user=current_user,
            group_id=group_id
        )
        return entity.get_options()

    @restaurant_required
    def post(self, group_id):
        data = validate_request(MenuOptionSchema, request.get_json())
        entity = MenuOptionListEntity(
            current_user=current_user,
            group_id=group_id
        )
        return entity.create_option(data)


class MenuOptionResource(Resource):
    endpoint = 'api.MenuOptionResource'

    @restaurant_required
    def put(self, menu_option_id):
        data = validate_request(MenuOptionSchema, request.get_json())
        entity = MenuOptionEntity(
            current_user=current_user,
            menu_option_id=menu_option_id
        )
        return entity.update_menu_option(data)

    @restaurant_required
    def delete(self, menu_option_id):
        entity = MenuOptionEntity(
            current_user=current_user,
            menu_option_id=menu_option_id
        )
        return entity.delete_menu_option()


class DeliveryZoneListResource(Resource):
    endpoint = 'api.DeliveryZoneListResource'

    @restaurant_required
    def get(self, restaurant_id):
        entity = DeliveryZoneListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_delivery_zones()

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(DeliveryZoneSchema, request.get_json())
        entity = DeliveryZoneListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_delivery_zone(data)

class DeliveryZoneResource(Resource):
    endpoint = 'api.DeliveryZoneResource'

    @restaurant_required
    def put(self, delivery_zone_id):
        data = validate_request(DeliveryZoneSchema, request.get_json())
        entity = DeliveryZoneEntity(
            current_user=current_user,
            delivery_zone_id=delivery_zone_id
        )
        return entity.update_delivery_zone(data)

    @restaurant_required
    def delete(self, delivery_zone_id):
        entity = DeliveryZoneEntity(
            current_user=current_user,
            delivery_zone_id=delivery_zone_id
        )
        return entity.delete_delivery_zone()

class DeliveryPolygonListResource(Resource):
    endpoint = 'api.DeliveryPolygonListResource'
    """
    多边形集合接口
    - POST: 创建多边形
    """
    @admin_required
    def post(self, zone_id):
        # 校验请求参数
        data = validate_request(DeliveryPolygonCreateSchema, request.get_json())
        entity = DeliveryPolygonListEntity(
            current_user=current_user,
            zone_id=zone_id
        )
        return entity.create_polygon(data)


class DeliveryPolygonResource(Resource):
    endpoint = 'api.DeliveryPolygonResource'
    """
    单个多边形接口
    - GET: 获取多边形详情
    - DELETE: 删除多边形
    """
    @restaurant_required
    def get(self, polygon_id):
        entity = DeliveryPolygonEntity(
            current_user=current_user,
            polygon_id=polygon_id
        )
        return entity.get_polygon(polygon_id)

    @admin_required
    def delete(self, polygon_id):
        entity = DeliveryPolygonEntity(
            current_user=current_user,
            polygon_id=polygon_id
        )
        return entity.delete_polygon(polygon_id)

class OperatingHoursListResource(Resource):
    endpoint = 'api.OperatingHoursListResource'

    @restaurant_required
    def get(self, restaurant_id):
        entity = OperatingHoursListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_operating_hour()

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(OperatingHoursSchema, request.get_json())
        entity = OperatingHoursListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_operating_hour(data)


class OperatingHoursResource(Resource):
    endpoint = 'api.OperatingHoursResource'

    @restaurant_required
    def put(self, operating_hours_id):
        data = validate_request(UpdateOperatingHoursSchema, request.get_json())
        entity = OperatingHoursEntity(
            current_user=current_user,
            operating_hours_id=operating_hours_id
        )
        return entity.update_operating_hour(data)

    @restaurant_required
    def delete(self, operating_hours_id):
        entity = OperatingHoursEntity(
            current_user=current_user,
            operating_hours_id=operating_hours_id
        )
        return entity.delete_operating_hour()


class PromotionListResource(Resource):
    endpoint = 'api.PromotionListResource'

    @restaurant_required
    def get(self, restaurant_id):
        entity = PromotionListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_promotion()

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(PromotionSchema, request.get_json())
        entity = PromotionListEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.post_promotion(data)


class PromotionResource(Resource):
    endpoint = 'api.PromotionResource'

    @restaurant_required
    def put(self, promotion_id):
        data = validate_request(UpdatePromotionSchema, request.get_json())
        entity = PromotionEntity(
            current_user=current_user,
            promotion_id=promotion_id
        )
        return entity.update_promotion(data)

    @restaurant_required
    def delete(self, promotion_id):
        entity = PromotionEntity(
            current_user=current_user,
            promotion_id=promotion_id
        )
        return entity.delete_promotion()

class RestaurantStatisticsListResource(Resource):
    """
    餐馆统计信息接口（历史数据）
    - GET: 获取某餐馆的所有统计历史数据
    """
    @restaurant_required
    def get(self, restaurant_id):
        entity = RestaurantStatisticsEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )

        return entity.list_statistics()

class RestaurantStatisticsResource(Resource):
    """
    餐馆统计信息接口（单个餐馆）
    - GET: 获取某餐馆的统计数据
    """
    @restaurant_required
    def get(self, restaurant_id):
        date = request.args.get("date")  # 可选参数
        entity = RestaurantStatisticsEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.get_statistics(date)

