# -*- coding: utf-8 -*-
from datetime import datetime

from flask import request
from flask_restful import Resource
from app.routes.jwt import rider_required, current_user
from app.routes.logger import logger
from app.routes.riders.entities import RiderEntity, RiderItemEntity, RiderLocationEntity, NearbyRidersEntity
from app.schemas.rider.rider_schema import RiderSchema, UpdateRiderSchema, RiderLoginSchema, RiderLocationSchema, \
    GetNearbySchema
from app.utils.validation import validate_request


class RiderListResource(Resource):
    endpoint='api.RiderListResource'

    @rider_required
    def get(self):
        entity = RiderEntity(current_user=current_user)
        return entity.get_all_riders()

    @rider_required
    def post(self):
        data = validate_request(RiderSchema, request.get_json())
        entity = RiderEntity(current_user=current_user)
        return entity.create_rider(data)

class RiderResource(Resource):
    endpoint='api.RiderResource'

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

    @rider_required
    def delete(self, rider_id):
        entity = RiderItemEntity(
            current_user=current_user,
            rider_id=rider_id
        )
        return entity.delete_rider()


class RiderLoginResource(Resource):
    endpoint='api.RiderLoginResource'

    @rider_required
    def post(self):
        data = validate_request(RiderLoginSchema, request.get_json())
        entity = RiderEntity()
        return entity.rider_login(data)

class RiderLocationResource(Resource):
    """骑手实时位置接口"""

    @rider_required
    def post(self, rider_id):
        """上传位置"""
        data = validate_request(RiderLocationSchema, request.get_json())
        entity = RiderLocationEntity(
            current_user=current_user,
            rider_id=rider_id)
        return entity.create_location(data)

    @rider_required
    def get(self, rider_id):
        """获取最新位置"""
        entity = RiderLocationEntity(
            current_user=current_user,
            rider_id=rider_id)
        return entity.get_latest_location()


class RiderLocationHistoryResource(Resource):
    """历史位置"""

    @rider_required
    def get(self, rider_id):
        entity = RiderLocationEntity(
            current_user=current_user,
            rider_id=rider_id)
        return entity.get_location_history()


class NearbyRidersResource(Resource):
    """管理员获取附近骑手"""

    @rider_required
    def get(self):
        args = validate_request(GetNearbySchema, request.args)
        entity = NearbyRidersEntity(current_user=current_user)
        return entity.get_nearby_riders(
            lat=args["lat"],
            lon=args["lon"],
            radius=args.get("radius", 2000),
        )




