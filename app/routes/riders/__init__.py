# -*- coding: utf-8 -*-
from app.routes.riders.resources import RiderListResource, RiderResource, RiderLoginResource, RiderLocationResource


def register_rider_routes(api):
    api.add_resource(RiderListResource, '/rider')  #  骑手
    api.add_resource(RiderResource, '/rider/<int:rider_id>')  #  骑手详情
    api.add_resource(RiderLoginResource, '/rider/login') #  骑手登录
    api.add_resource(RiderLocationResource, '/rider/<int:rider_id>/location') #  骑手实时位置

    return [
        'api.RiderListResource',
        'api.RiderResource',
        'api.RiderLoginResource',
        'api.RiderLocationResource'


    ]