# -*- coding: utf-8 -*-
from datetime import datetime

from flask import request
from flask_restful import Resource, reqparse

from app.routes.jwt import rider_required, current_user
from app.routes.logger import logger
from app.routes.riders.entities import RiderEntity, RiderItemEntity, RiderLocationEntity
from app.schemas.rider.rider_schema import RiderSchema, UpdateRiderSchema, RiderLoginSchema, RiderLocationSchema
from app.utils.validation import validate_request, BusinessValidationError
from lib.ecode import ECode
import socketio

class RiderListResource(Resource):
    endpoint='api.RiderListResource'

    @rider_required
    def get(self):
        entity=RiderEntity(current_user=current_user)
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
    endpoint='api.RiderLocationResource'

    @rider_required
    def post(self, rider_id):
        """创建位置记录"""
        try:
            data = validate_request(RiderLocationSchema, request.get_json())
            entity = RiderLocationEntity(
                current_user=current_user,
                rider_id=rider_id
            )
            entity.create_location(data)

            # 通过WebSocket实时推送
            socketio.emit('location_update', {
                'rider_id': rider_id,
                'location': data
            }, room=f"rider_{rider_id}")

            return entity.create_location(data), ECode.SUCC

        except BusinessValidationError as e:
            return {"message": e.message}
        except Exception as e:
            logger.error(f"创建位置记录异常: {str(e)}")
            return {"message": "创建位置记录失败"}, ECode.ERROR


class RiderLatestLocation(Resource):

    def get(self, rider_id):
        """获取最新位置"""
        try:
            entity = RiderLocationEntity(current_user=current_user, rider_id=rider_id)
            return entity.get_current_location(), ECode.SUCC

        except BusinessValidationError as e:
            return {"message": e.message}
        except Exception as e:
            logger.error(f"获取最新位置异常: {str(e)}")
            return {"message": "获取最新位置失败"}, ECode.ERROR


class NearbyRiders(Resource):
    def get(self):
        """管理员获取附近骑手"""
        try:
            latitude = request.args.get('latitude', type=float)
            longitude = request.args.get('longitude', type=float)
            radius = request.args.get('radius', 5000, type=int)
            limit = request.args.get('limit', 20, type=int)
            online_only = request.args.get('online_only', True, type=bool)

            if not latitude or not longitude:
                raise BusinessValidationError("需要经纬度参数", ECode.ERROR)

            entity = RiderLocationEntity(current_user=current_user)

            return entity.get_nearby_riders(latitude, longitude, radius, limit, online_only)

        except BusinessValidationError as e:
            return {"message": e.message}
        except Exception as e:
            logger.error(f"获取附近骑手异常: {str(e)}")
            return {"message": "获取附近骑手失败"}, ECode.ERROR


class RiderLocationHistoryResource(Resource):
    """骑手位置历史资源"""
    def get(self, rider_id):
        try:
            limit = request.args.get('limit', 100, type=int) # 限制返回记录数，默认100
            start_time = request.args.get('start_time')
            end_time = request.args.get('end_time')

            # 转换时间格式
            if start_time:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if end_time:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            entity = RiderLocationEntity(current_user=current_user, rider_id=rider_id)

            return entity.get_rider_locations(rider_id, limit, start_time, end_time)

        except BusinessValidationError as e:
            return {"message": e.message}
        except Exception as e:
            logger.error(f"获取位置历史异常: {str(e)}")
            return {"message": "获取位置历史失败"}, ECode.ERROR




