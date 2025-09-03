# -*- coding: utf-8 -*-
from app.routes.riders.resources import RiderListResource, RiderResource, RiderLoginResource, RiderLocationResource, \
    RiderLocationHistoryResource, NearbyRidersResource


def register_rider_routes(api):
    api.add_resource(RiderListResource, '/rider')  # 骑手
    api.add_resource(RiderResource, '/rider/<int:rider_id>')  # 骑手详情
    api.add_resource(RiderLoginResource, '/rider/login')  # 骑手注销
    api.add_resource(RiderLoginResource, '/rider/login')  # 开始接单
    api.add_resource(NearbyRidersResource, "/riders/nearby")  # 骑手停止接单
    # api.add_resource(RiderLocationResource, "/riders/<int:rider_id>/location")
    api.add_resource(RiderLocationHistoryResource, "/riders/<int:rider_id>/locations")  # 历史位置
    # api.add_resource(NearbyRidersResource, "/riders/nearby")
    # 骑手在开始接单之后才开启socket任务

    return [
        'api.RiderListResource',
        'api.RiderResource',
        'api.RiderLoginResource',
        'api.RiderLocationResource',
        'api.RiderLocationHistoryResource',
        'api.NearbyRidersResource'
    ]
