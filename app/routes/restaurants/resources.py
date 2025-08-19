# -*- coding: utf-8 -*-
from flask import request
from flask_jwt_extended import current_user
from flask_restful import Resource

from app.routes.restaurants.entities import RestaurantEntity, RestaurantItemEntity, MenuItemEnity
from app.schemas.restaurants.restaurant_schema import Restaurant, RestaurantLoginSchema, UpdateRestaurant
from app.schemas.schemas import MenuItemSchema
from app.utils.validation import  validate_request



class RestaurantListResource(Resource):
    endpoint = 'api.RestaurantListResource'

    def get(self):
        entity = RestaurantEntity(current_user=current_user)
        return entity.get_restaurants(**request.args)

    def post(self):
        data = validate_request(Restaurant, request.get_json())
        entity = RestaurantEntity(current_user=getattr(self, 'current_user', None))
        return  entity.create_restaurant(data)


class RestaurantResource(Resource):
    endpoint = 'api.RestaurantResource'

    def get(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id = restaurant_id
        )
        return entity.get_restaurant()

    def put(self, restaurant_id):
        data = validate_request(UpdateRestaurant, request.get_json())
        entity = RestaurantItemEntity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id = restaurant_id
        )
        return entity.update_restaurant(data)

    def delete(self, restaurant_id):
        entity = RestaurantItemEntity(
            current_user=getattr(self, 'current_user', None),
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
    def post(self):
        data = validate_request(MenuItemSchema, request.get_json())
        entity = MenuItemEnity()
        return entity.create_menu(data)

    def get(self, restaurant_id,menuitem_id):
        entity = MenuItemEnity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id = restaurant_id
        )
        return entity.get_menuitem(menuitem_id)
    def put(self, restaurant_id):
        data = validate_request(MenuItemSchema, request.get_json())
        entity = MenuItemEnity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id = restaurant_id
        )
        return entity.update_menuitem(data)

    def delete(self,restaurant_id, menuitem_id):
        entity = MenuItemEnity(
            current_user=getattr(self, 'current_user', None),
            restaurant_id = restaurant_id,
        )
        return entity.delete_menuitem(menuitem_id)
