# -*- coding: utf-8 -*-
from datetime import datetime
from flask import request
from flask_restful import Resource
from app.models.orders import Order
from app.routes.jwt import admin_required, current_user, user_required, restaurant_required, rider_required
from app.routes.orders.entities import OrderEntity, OrderItemEntity
from app.schemas.orders.orders_schema import OrderSchemas, OrderUpdateSchemas, OrderAssignmentSchema
from app.utils.validation import validate_request


class OrderListResource(Resource):
    endpoint = 'api.OrderListResource'

    @user_required
    def get(self):
        """获取订单列表"""
        entity = OrderEntity(current_user=current_user)
        status = request.args.get('status')
        restaurant_id = request.args.get('restaurant_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        filters = {}
        if status: filters['status'] = status
        if restaurant_id: filters['restaurant_id'] = int(restaurant_id)
        if start_date:
            try:
                filters['start_date'] = datetime.fromisoformat(start_date)
            except ValueError:
                pass
        if end_date:
            try:
                filters['end_date'] = datetime.fromisoformat(end_date)
            except ValueError:
                pass

        return entity.get_orders(**filters)

    @user_required
    def post(self):
        """创建新订单"""
        data = validate_request(OrderSchemas, request.get_json())
        entity = OrderEntity(current_user=current_user)
        return entity.create_order(data)


class OrderResource(Resource):
    endpoint = 'api.OrderResource'

    @user_required
    def get(self, order_id):
        """获取订单详情"""
        entity = OrderEntity(current_user=current_user)
        return entity.get_order(order_id)

    @admin_required
    def put(self, order_id):
        """更新订单状态"""
        data = validate_request(OrderUpdateSchemas, request.get_json())
        entity = OrderEntity(current_user=current_user)
        return entity.update_order_status(order_id, data['status'], data.get('note'))

    @user_required
    def delete(self, order_id):
        """取消订单"""
        entity = OrderEntity(current_user=current_user)
        return entity.update_order_status(order_id, Order.STATUS_CANCELED, "Order canceled by user")

class OrderRestaurantResource(Resource):
    endpoint = 'api.OrderRestaurantResource'

    @restaurant_required
    def get(self, order_id):
        """餐馆获取订单详情"""
        entity = OrderEntity(current_user=current_user)
        return entity.get_order(order_id)

    @restaurant_required
    def put(self, order_id):
        """餐馆更新订单状态"""
        data = validate_request(OrderUpdateSchemas, request.get_json())
        entity = OrderEntity(current_user=current_user)
        return entity.update_order_status(order_id, data['status'], data.get('note'))

class OrderRiderResource(Resource):
    endpoint = 'api.OrderRestaurantResource'

    @rider_required
    def put(self, order_id):
        """骑手更新订单状态"""
        data = validate_request(OrderUpdateSchemas, request.get_json())
        entity = OrderEntity(current_user=current_user)
        return entity.update_order_status(order_id, data['status'], data.get('note'))


class OrderAssignmentResource(Resource):
    endpoint = 'api.OrderAssignmentResource'

    # 管理员权限可以手动分配骑手，程序可以自动分派骑手
    @admin_required
    @restaurant_required  # 商家自行配送
    def post(self, order_id):
        """分配订单给骑手（手动或自动）"""
        data = request.get_json() or {}

        # 如果提供了rider_id，则手动分配；否则自动分配
        if 'rider_id' in data:
            data = validate_request(OrderAssignmentSchema, data)
            entity = OrderEntity(current_user=current_user)
            return entity.assign_rider(order_id, data['rider_id'])
        # else:
        #     entity = OrderEntity(current_user=current_user)
        #     return entity.auto_assign_rider(order_id)


class OrderItemsResource(Resource):
    endpoint = 'api.OrderItemsResource'

    @user_required
    def get(self, order_id):
        """获取订单项列表"""
        entity = OrderItemEntity(current_user=current_user, order_id=order_id)
        return entity.get_items()


class OrderAutoAssignmentResource(Resource):
    endpoint = 'api.OrderAutoAssignmentResource'

    @admin_required
    @restaurant_required
    def post(self, order_id):
        """自动分配订单给最优骑手"""
        entity = OrderEntity(current_user=current_user)
        return entity.auto_assign_rider(order_id)
