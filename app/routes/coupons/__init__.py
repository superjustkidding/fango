# -*- coding: utf-8 -*-

from app.routes.coupons.resources import CouponResource, CouponListResource, CouponAssignResource


def register_coupon_routes(api):
    api.add_resource(CouponResource, '/coupons')  # 获取创建优惠券
    api.add_resource(CouponAssignResource, '/coupons/assign/<int:coupon_id>')  # 发放优惠券
    api.add_resource(CouponListResource, '/coupons/<int:coupon_id>')  # 更新删除优惠券

    return {
        'api.CouponResource',
        'api.CouponListResource',
        'api.CouponAssignResource'
    }