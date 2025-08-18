from flask import request
from flask_jwt_extended import current_user
from flask_restful import Resource

from app.routes.restaurants.entities import RestaurantEntity, RestaurantItemEntity
from app.schemas.restaurants.restaurant_schema import RestaurantBase
from app.utils.validation import BusinessValidationError, validate_request
from lib.ecode import ECode


class RestaurantListResource(Resource):
    endpoint = 'api.RestaurantListResource'

    def get(self):
        if not current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        entity = RestaurantEntity(current_user=current_user)
        return entity.get_restaurants(**request.args)

    def post(self):
        data = validate_request(RestaurantBase, request.get_json())
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
        data = validate_request(RestaurantBase, request.get_json())
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





