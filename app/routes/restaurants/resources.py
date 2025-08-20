# -*- coding: utf-8 -*-
from flask import request

from flask_restful import Resource
from app.routes.restaurants.entities import RestaurantEntity, RestaurantItemEntity, MenuItemListEntity, \
    MenuCategoryEntity, MenuItemEntity
from app.schemas.restaurants.restaurant_schema import Restaurant, RestaurantLoginSchema, UpdateRestaurant, \
    MenuCategorySchema, UpdateMenuItemSchema, MenuItemSchema
from app.utils.validation import validate_request
from app.routes.jwt import current_user, restaurant_required


class RestaurantListResource(Resource):
    endpoint = 'api.RestaurantListResource'

    @restaurant_required
    def get(self):
        entity = RestaurantEntity(current_user=current_user)
        return entity.get_restaurants(**request.args)

    @restaurant_required
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
        return entity.delete_resaurant()


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
        return entity.get_menuitems()

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
        return entity.delete_menuitem(menuitem_id)


class MenuCategoryResource(Resource):
    endpoint = 'api.MenuCategoryResource'

    @restaurant_required
    def post(self, restaurant_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_menu_category(data)

    @restaurant_required
    def get(self, restaurant_id):
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id)
        return entity.get_menu_category(restaurant_id)

    @restaurant_required
    def put(self, restaurant_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.update_menu_category(data)

    @restaurant_required
    def delete(self, restaurant_id):
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.delete_menu_category()


