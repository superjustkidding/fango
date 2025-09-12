# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource

from app.routes.coupons.entities import CouponEntity, CouponAssignEntity, CouponListEntity
from app.routes.jwt import admin_required, current_user
from app.schemas.coupon.coupon_schema import CouponSchema, CouponUpdateSchema
from app.utils.validation import validate_request


class CouponResource(Resource):
    endpoint = 'api.CouponResource'

    @admin_required
    def post(self):
        data = validate_request(CouponSchema, request.get_json())
        entity = CouponEntity(current_user=current_user)
        return entity.create_coupon(data)

    @admin_required
    def get(self):
        entity = CouponEntity(current_user=current_user)
        return entity.get_all_coupons()

class CouponAssignResource(Resource):
    endpoint = 'api.CouponAssignResource'

    @admin_required
    def post(self, coupon_id):
        data = request.get_json() or {}
        entity = CouponAssignEntity(coupon_id=coupon_id)
        if 'user_id' in data:
            return entity.assign_user_single(data['user_id'])
        elif data.get('auto'):
            return entity.auto_assign_coupon()
        return None

class CouponListResource(Resource):
    endpoint = 'api.CouponListResource'

    @admin_required
    def put(self, coupon_id):
        data = validate_request(CouponUpdateSchema, request.get_json())
        entity = CouponListEntity(coupon_id=coupon_id)
        return entity.update_coupon(data)

    @admin_required
    def delete(self, coupon_id):
        entity = CouponListEntity(coupon_id=coupon_id)
        return entity.delete_coupon()

