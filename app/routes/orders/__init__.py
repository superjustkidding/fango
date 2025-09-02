# -*- coding: utf-8 -*-
from app.routes.orders.resources import (OrderListResource, OrderResource, OrderAssignmentResource,
                                         OrderItemsResource, OrderAutoAssignmentResource, OrderRestaurantResource,
                                         OrderRiderResource)

def register_order_routes(api):
    api.add_resource(OrderListResource, '/orders')  # 订单创建列表
    api.add_resource(OrderResource, '/orders/<int:order_id>')  # 订单详情修改删除
    api.add_resource(OrderAssignmentResource, '/orders/<int:order_id>/assign')  # 管理员或者餐馆指定骑手
    api.add_resource(OrderAutoAssignmentResource, '/orders/<int:order_id>/assign_auto')  # 自动分派订单骑手
    api.add_resource(OrderItemsResource, '/orders/<int:order_id>/items')  # 用户订单列表
    api.add_resource(OrderRestaurantResource, '/orders/restaurant/<int:order_id>')  # 餐馆修改订单获取详情
    api.add_resource(OrderRiderResource, '/orders/rider/<int:order_id>')  # 骑手修改订单

    return [
        'api.OrderListResource',
        'api.OrderResource',
        'api.OrderAssignmentResource',
        'api.OrderItemsResource'
    ]
