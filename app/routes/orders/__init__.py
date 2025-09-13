# -*- coding: utf-8 -*-
from app.routes.orders.resources import OrderListResource, OrderResource, OrderAssignmentResource, \
    OrderAutoAssignmentResource, OrderItemsResource, OrderRestaurantResource, OrderRiderResource, OrderReviewResource, \
    OrderReviewListResource


def register_order_routes(api):
    api.add_resource(OrderListResource, '/orders')  # 订单创建列表
    api.add_resource(OrderResource, '/orders/<int:order_id>')  # 订单详情修改删除
    api.add_resource(OrderAssignmentResource, '/orders/<int:order_id>/assign')  # 管理员或者餐馆指派骑手
    api.add_resource(OrderAutoAssignmentResource, '/orders/<int:order_id>/auto')  # 自动分派订单骑手
    api.add_resource(OrderItemsResource, '/orders/<int:order_id>/item')  # 用户订单列表
    api.add_resource(OrderRestaurantResource, '/orders/<int:order_id>/restaurant')  # 餐馆修改订单获取详情
    api.add_resource(OrderRiderResource, '/orders/<int:order_id>/rider')  # 骑手修改订单
    api.add_resource(OrderReviewResource, '/orders/<int:order_id>/review')  # 订单评价
    api.add_resource(OrderReviewListResource, '/orders/reply/<int:review_id>')

    return [
        'api.OrderListResource',
        'api.OrderResource',
        'api.OrderAssignmentResource',
        'api.OrderAutoAssignmentResource',
        'api.OrderItemsResource',
        'api.OrderRestaurantResource',
        'api.OrderRiderResource',
        'api.OrderReviewResource',
        'api.OrderReviewListResource',
        ]