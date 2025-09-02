# -*- coding: utf-8 -*-
from datetime import datetime

from flask import request
from flask_restful import Resource
from app.routes.jwt import rider_required, current_user, admin_required
from app.routes.riders.entities import RiderEntity, RiderItemEntity, RiderLocationEntity, NearbyRidersEntity, \
    RiderAssignmentEntity
from app.schemas.rider.rider_schema import RiderSchema, UpdateRiderSchema, RiderLoginSchema, RiderLocationSchema, \
    GetNearbySchema
from app.utils.validation import validate_request


class RiderListResource(Resource):
    endpoint = 'api.RiderListResource'

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
        limit = request.args.get("limit", 50, type=int)
        entity = RiderLocationEntity(
            current_user=current_user,
            rider_id=rider_id)
        return entity.get_location_history(limit)


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

class RiderAssignmentResource(Resource):
    """骑手订单分配接口"""

    @admin_required
    def post(self, order_id):
        """
        分配订单给骑手
        body: { "rider_id": 123 }
        """
        data = request.get_json()
        rider_id = data.get("rider_id")
        entity = RiderAssignmentEntity(current_user=current_user, order_id=order_id)
        result, code = entity.assign_order(rider_id)
        return {"code": code, "data": result}

    @rider_required
    def put(self, order_id, rider_id):
        """
        骑手响应订单分配
        body: { "accept": true/false }
        """
        data = request.get_json()
        accept = data.get("accept", True)
        entity = RiderAssignmentEntity(current_user=current_user, order_id=order_id, rider_id=rider_id)
        result, code = entity.respond_assignment(accept)
        return {"code": code, "data": result}

    @admin_required
    def delete(self, order_id, rider_id):
        """
        取消订单分配
        """
        entity = RiderAssignmentEntity(current_user=current_user, order_id=order_id, rider_id=rider_id)
        result, code = entity.cancel_assignment()
        return {"code": code, "data": result}



