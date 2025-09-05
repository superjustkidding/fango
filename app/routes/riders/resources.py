# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from app.routes.jwt import rider_required, current_user, admin_required
from app.routes.riders.entities import RiderEntity, RiderItemEntity, RiderLocationEntity
from app.schemas.rider.rider_schema import RiderSchema, UpdateRiderSchema, RiderLoginSchema

from app.utils.validation import validate_request


class RiderListResource(Resource):
    endpoint = 'api.RiderListResource'

    @admin_required
    def get(self):
        entity = RiderEntity(current_user=current_user)
        return entity.get_all_riders()

    def post(self):
        data = validate_request(RiderSchema, request.get_json())
        entity = RiderEntity(current_user=current_user)
        return entity.create_rider(data)

class RiderResource(Resource):
    endpoint = 'api.RiderResource'

    @rider_required
    def get(self, rider_id):
        entity = RiderItemEntity(
            current_user=current_user,
            rider_id=rider_id
        )
        return entity.get_rider()

    @rider_required
    def put(self, rider_id):
        data = validate_request(UpdateRiderSchema, request.get_json())
        entity = RiderItemEntity(
            current_user=current_user,
            rider_id=rider_id
        )
        return entity.update_rider(data)

    @admin_required
    def delete(self, rider_id):
        entity = RiderItemEntity(
            current_user=current_user,
            rider_id=rider_id
        )
        return entity.delete_rider()


class RiderLoginResource(Resource):
    endpoint='api.RiderLoginResource'
    """登录"""
    def post(self):
        data = validate_request(RiderLoginSchema, request.get_json())
        entity = RiderEntity(data)
        return entity.rider_login(data)

class RiderLogoutResource(Resource):
    endpoint='api.RiderLogoutResource'
    """退出"""
    @rider_required
    def post(self):
        entity = RiderEntity(current_user=current_user)
        return entity.rider_logout()

class RiderStartOrdersResource(Resource):
    endpoint = 'api.RiderStartOrdersResource'

    @rider_required
    def post(self):
        """骑手开始接单"""
        entity = RiderEntity(current_user=current_user)
        return entity.start_taking_orders()


class RiderStopOrdersResource(Resource):
    endpoint = 'api.RiderStopOrdersResource'

    @rider_required
    def post(self):
        """骑手停止接单"""
        entity = RiderEntity(current_user=current_user)
        return entity.stop_taking_orders()


class RiderLocationHistoryResource(Resource):
    """历史位置"""

    @rider_required
    def get(self, rider_id):
        limit = request.args.get("limit", 50, type=int)
        entity = RiderLocationEntity(
            current_user=current_user,
            rider_id=rider_id)
        return entity.get_location_history(limit)























