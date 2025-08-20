# -*- coding: utf-8 -*-
from flask import request
from flask_jwt_extended import current_user, get_current_user
from flask_restful import Resource

from app.routes.restaurants.entities import RestaurantEntity, RestaurantItemEntity,  MenuItemEntity, MenuCategoryEntity
from app.schemas.restaurants.restaurant_schema import Restaurant, RestaurantLoginSchema, UpdateRestaurant, \
    MenuCategorySchema, UpdateMenuItemSchema, MenuItemSchema
from app.utils.validation import validate_request
from flask_jwt_extended import jwt_required, current_user


class RestaurantListResource(Resource):
    endpoint = 'api.RestaurantListResource'


    def get(self):
        entity = RestaurantEntity(current_user=current_user)
        return entity.get_restaurants(**request.args)


    def post(self):
        data = validate_request(Restaurant, request.get_json())
        entity = RestaurantEntity(current_user=current_user)
        return entity.create_restaurant(data)


class RestaurantResource(Resource):
    endpoint = 'api.RestaurantResource'

    def get(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user= current_user ,
            restaurant_id=restaurant_id
        )
        return entity.get_restaurant()

    def put(self, restaurant_id):
        data = validate_request(UpdateRestaurant, request.get_json())
        entity = RestaurantItemEntity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id=restaurant_id
        )
        return entity.update_restaurant(data)

    def delete(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user= current_user,
            restaurant_id=restaurant_id
        )
        return entity.delete_resaurant()


class RestaurantLoginResource(Resource):
    endpoint = 'api.RestaurantLoginResource'

    def post(self):
        data = validate_request(RestaurantLoginSchema, request.get_json())
        entity = RestaurantEntity()
        return entity.Rlogin(data)


class MenuItemResource(Resource):
    endpoint = 'api.MenuItemResource'

    @jwt_required()
    def post(self, restaurant_id):
        current_user = get_current_user()
        data = validate_request(MenuItemSchema, request.get_json())
        entity = MenuItemEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_menu(data)


    def get(self, menuitem_id):
        entity = MenuItemEntity(
            current_user= current_user,
            menuitem_id= menuitem_id
        )
        return entity.get_menuitem(menuitem_id)


    def put(self, menuitem_id):
        data = validate_request(UpdateMenuItemSchema, request.get_json())
        entity = MenuItemEntity(
            current_user= current_user,
            menuitem_id = menuitem_id
        )
        return entity.update_menuitem(data)


    def delete(self, menuitem_id):
        entity = MenuItemEntity(
            current_user=current_user,
            menuitem_id = menuitem_id
        )
        return entity.delete_menuitem(menuitem_id)


class MenuCategoryResource(Resource):
    endpoint = 'api.MenuCategoryResource'

    def post(self, restaurant_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.create_menu_category(data)

    def get(self, restaurant_id):
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id)
        return entity.get_menu_category(restaurant_id)

    def put(self, restaurant_id):
        data = validate_request(MenuCategorySchema, request.get_json())
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.update_menu_category(data)

    def delete(self, restaurant_id):
        entity = MenuCategoryEntity(
            current_user=current_user,
            restaurant_id=restaurant_id
        )
        return entity.delete_menu_category()


