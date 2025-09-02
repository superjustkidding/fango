# -*- coding: utf-8 -*-
import json
from datetime import datetime
from app import db
from app.models import Order, OrderItem, OrderItemOption, OrderStatusHistory, RiderAssignment, Rider
from app.utils.validation import BusinessValidationError
from app.utils.websocket import redis_client, socketio, TASK_ASSIGNMENT_CHANNEL
from lib.ecode import ECode
from app.utils.geo import haversine


class OrderEntity:
    def __init__(self, current_user):
        self.current_user = current_user

    def create_order(self, data):
        """创建新订单"""
        # 验证用户权限
        if not self.current_user:
            raise BusinessValidationError("Authentication required", ECode.AUTH)

        # 创建订单
        order = Order(
            user_id=self.current_user.id,
            restaurant_id=data['restaurant_id'],
            total_amount=data['total_amount'],
            delivery_fee=data.get('delivery_fee', 0),
            discount_amount=data.get('discount_amount', 0),
            final_amount=data['final_amount'],
            delivery_address=data['delivery_address'],
            special_instructions=data.get('special_instructions'),
            status=Order.STATUS_PENDING,
            estimated_preparation_time=data.get('estimated_preparation_time')
        )

        db.session.add(order)
        db.session.flush()  # 获取订单ID但不提交

        # 添加订单项
        for item_data in data.get('items', []):
            item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data['menu_item_id'],
                quantity=item_data['quantity'],
                price_at_order=item_data['price_at_order'],
                special_instructions=item_data.get('special_instructions')
            )
            db.session.add(item)

            # 处理选项
            for option_data in item_data.get('options', []):
                option = OrderItemOption(
                    order_item_id=item.id,
                    option_id=option_data['option_id']
                )
                db.session.add(option)

        # 添加初始状态历史
        status_history = OrderStatusHistory(
            order_id=order.id,
            status=Order.STATUS_PENDING,
            actor_id=self.current_user.id,
            actor_type='user',
            note='Order created'
        )
        db.session.add(status_history)

        db.session.commit()

        # 发布订单创建事件
        redis_client.publish('new_orders', json.dumps(order.to_dict()))

        return order.to_dict(), ECode.SUCC

    def get_orders(self, **filters):
        """获取订单列表"""
        query = Order.query.filter_by(deleted=False)

        # 权限检查：用户只能查看自己的订单
        if not self.current_user.is_admin:
            query = query.filter(Order.user_id == self.current_user.id)

        # 应用过滤器
        if 'status' in filters:
            query = query.filter(Order.status == filters['status'])

        if 'restaurant_id' in filters:
            query = query.filter(Order.restaurant_id == filters['restaurant_id'])

        if 'start_date' in filters:
            query = query.filter(Order.created_at >= filters['start_date'])

        if 'end_date' in filters:
            query = query.filter(Order.created_at <= filters['end_date'])

        # 排序
        query = query.order_by(Order.created_at.desc())

        orders = query.all()
        return [order.to_dict() for order in orders], ECode.SUCC

    def get_order(self, order_id):
        """获取单个订单详情"""
        order = Order.query.filter_by(id=order_id, deleted=False).first()

        if not order:
            raise BusinessValidationError("Order not found", ECode.NOTFOUND)

        # 权限检查：用户只能查看自己的订单
        if not self.current_user.is_admin and order.user_id != self.current_user.id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        return order.to_dict(), ECode.SUCC

    def update_order_status(self, order_id, new_status, note=None):
        """更新订单状态"""
        order = Order.query.filter_by(id=order_id, deleted=False).first()
        if not order:
            raise BusinessValidationError("Order not found", ECode.NOTFOUND)

        # 权限检查：用户只能取消自己的订单，餐厅和管理员可以更新状态
        if (new_status == Order.STATUS_CANCELED and
                not self.current_user.is_admin and
                self.current_user.id != order.user_id):
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        # 更新订单状态
        order.status = new_status

        # 添加状态历史
        status_history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            actor_id=self.current_user.id,
            actor_type=self.current_user.__class__.__name__.lower(),
            note=note or f"Status changed to {new_status}"
        )
        db.session.add(status_history)

        db.session.commit()

        # 发布状态更新事件
        socketio.emit('order_status_update', {
            'order_id': order.id,
            'status': new_status,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"order_{order.id}")

        return order.to_dict(), ECode.SUCC

    def find_optimal_rider(self, restaurant_lat, restaurant_lon, radius=5000):
        """查找最优骑手：基于距离和订单负载"""
        # 获取附近在线骑手
        nearby_riders = self.get_nearby_riders(restaurant_lat, restaurant_lon, radius)

        if not nearby_riders:
            return None

        # 获取骑手的当前订单负载
        rider_loads = self.get_rider_order_loads([rider['rider_id'] for rider in nearby_riders])

        # 计算每个骑手的得分（距离越近、负载越少，得分越高）
        scored_riders = []
        for rider in nearby_riders:
            rider_id = rider['rider_id']
            distance = rider['distance']
            load = rider_loads.get(rider_id, 0)

            # 计算得分（距离权重0.6，负载权重0.4）
            distance_score = 1.0 / (1.0 + distance / 1000)  # 距离越近得分越高
            load_score = 1.0 / (1.0 + load)  # 负载越少得分越高

            total_score = 0.6 * distance_score + 0.4 * load_score

            scored_riders.append({
                'rider_id': rider_id,
                'distance': distance,
                'load': load,
                'score': total_score
            })

        # 按得分排序，选择最优骑手
        scored_riders.sort(key=lambda x: x['score'], reverse=True)
        return scored_riders[0] if scored_riders else None

    def get_nearby_riders(self, lat, lon, radius=5000, limit=5):
        """获取附近的在线骑手（从Redis查询）"""
        nearby_riders = []

        # 获取所有在线骑手
        online_riders = Rider.query.filter_by(
            is_online=True,
            is_available=True,
            deleted=False
        ).all()

        for rider in online_riders:
            # 从Redis获取骑手最新位置
            latest_location = redis_client.zrevrange(f"rider_locations:{rider.id}", 0, 0)
            if not latest_location:
                continue

            location_data = json.loads(latest_location[0])
            rider_lat = location_data.get('latitude')
            rider_lon = location_data.get('longitude')

            if rider_lat is None or rider_lon is None:
                continue

            # 计算距离
            distance = haversine(lat, lon, rider_lat, rider_lon)

            # 检查是否在配送半径内
            if rider.delivery_radius and distance > rider.delivery_radius:
                continue

            # 添加到附近骑手列表
            nearby_riders.append({
                'rider_id': rider.id,
                'distance': distance,
                'location': {
                    'latitude': rider_lat,
                    'longitude': rider_lon
                }
            })

        # 按距离排序并限制数量
        nearby_riders.sort(key=lambda x: x['distance'])
        return nearby_riders[:limit]

    def get_rider_order_loads(self, rider_ids):
        """获取骑手的当前订单负载（正在进行的订单数量）"""
        loads = {}

        for rider_id in rider_ids:
            # 查询骑手正在进行的订单数量（状态为accepted且订单状态为preparing, ready或delivering）
            load_count = db.session.query(RiderAssignment).join(Order).filter(
                RiderAssignment.rider_id == rider_id,
                RiderAssignment.status == RiderAssignment.STATUS_ACCEPTED,
                Order.status.in_([Order.STATUS_PREPARING, Order.STATUS_READY, Order.STATUS_DELIVERING]),
                Order.deleted == False
            ).count()

            loads[rider_id] = load_count

        return loads

    def assign_rider(self, order_id, rider_id):
        """分配骑手给订单"""
        # 权限检查：只有管理员或餐厅可以分配骑手
        if not (self.current_user.is_admin or hasattr(self.current_user, 'restaurant_id')):
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        order = Order.query.filter_by(id=order_id, deleted=False).first()
        if not order:
            raise BusinessValidationError("Order not found", ECode.NOTFOUND)

        rider = Rider.query.filter_by(id=rider_id, deleted=False, is_online=True).first()
        if not rider:
            raise BusinessValidationError("Rider not available", ECode.NOTFOUND)

        # 创建骑手分配记录
        assignment = RiderAssignment(
            order_id=order_id,
            rider_id=rider_id,
            status=RiderAssignment.STATUS_PENDING
        )
        db.session.add(assignment)

        # 更新订单状态
        order.status = Order.STATUS_READY
        order.rider_id = rider_id

        # 添加状态历史
        status_history = OrderStatusHistory(
            order_id=order.id,
            status=Order.STATUS_READY,
            actor_id=self.current_user.id,
            actor_type=self.current_user.__class__.__name__.lower(),
            note=f"Rider {rider.name} assigned"
        )
        db.session.add(status_history)

        db.session.commit()

        # 通过WebSocket通知骑手
        socketio.emit('new_assignment', {
            'order_id': order.id,
            'restaurant_name': order.restaurant.name,
            'delivery_address': order.delivery_address,
            'estimated_preparation_time': order.estimated_preparation_time
        }, room=f"rider_{rider_id}")

        # 发布到Redis频道
        redis_client.publish(TASK_ASSIGNMENT_CHANNEL, json.dumps({
            'order_id': order.id,
            'rider_id': rider_id,
            'timestamp': datetime.utcnow().isoformat()
        }))

        return {
            'order': order.to_dict(),
            'assignment': assignment.to_dict()
        }, ECode.SUCC

    def auto_assign_rider(self, order_id):
        """自动分配骑手给订单"""
        order = Order.query.filter_by(id=order_id, deleted=False).first()
        if not order:
            raise BusinessValidationError("Order not found", ECode.NOTFOUND)

        # 获取餐厅位置（假设餐厅模型有latitude和longitude字段）
        restaurant = order.restaurant
        if not restaurant or not hasattr(restaurant, 'latitude') or not hasattr(restaurant, 'longitude'):
            raise BusinessValidationError("Restaurant location not available", ECode.REFRESH)

        # 查找最优骑手
        optimal_rider = self.find_optimal_rider(
            restaurant.latitude,
            restaurant.longitude,
            radius=5000  # 5公里范围内
        )

        if not optimal_rider:
            raise BusinessValidationError("No available riders nearby", ECode.NOTFOUND)

        rider_id = optimal_rider['rider_id']
        rider = Rider.query.filter_by(id=rider_id, deleted=False, is_online=True).first()
        if not rider:
            raise BusinessValidationError("Selected rider is no longer available", ECode.NOTFOUND)

        # 创建骑手分配记录
        assignment = RiderAssignment(
            order_id=order_id,
            rider_id=rider_id,
            status=RiderAssignment.STATUS_PENDING
        )
        db.session.add(assignment)

        # 更新订单状态
        order.status = Order.STATUS_READY
        order.rider_id = rider_id

        # 添加状态历史
        status_history = OrderStatusHistory(
            order_id=order.id,
            status=Order.STATUS_READY,
            actor_id=self.current_user.id,
            actor_type=self.current_user.__class__.__name__.lower(),
            note=f"Rider {rider.name} automatically assigned (distance: {optimal_rider['distance']:.2f}m, load: {optimal_rider['load']})"
        )
        db.session.add(status_history)
        db.session.commit()

        # 通过WebSocket通知骑手
        socketio.emit('new_assignment', {
            'order_id': order.id,
            'restaurant_name': order.restaurant.name,
            'delivery_address': order.delivery_address,
            'estimated_preparation_time': order.estimated_preparation_time,
            'auto_assigned': True
        }, room=f"rider_{rider_id}")

        # 发布到Redis频道
        redis_client.publish(TASK_ASSIGNMENT_CHANNEL, json.dumps({
            'order_id': order.id,
            'rider_id': rider_id,
            'timestamp': datetime.utcnow().isoformat(),
            'auto_assigned': True
        }))

        return {
            'order': order.to_dict(),
            'assignment': assignment.to_dict(),
            'rider': rider.to_dict(),
            'selection_info': {
                'distance': optimal_rider['distance'],
                'load': optimal_rider['load'],
                'score': optimal_rider['score']
            }
        }, ECode.SUCC


class OrderItemEntity:
    def __init__(self, current_user, order_id):
        self.current_user = current_user
        self.order_id = order_id
        self.order = Order.query.filter_by(id=order_id, deleted=False).first()

        if not self.order:
            raise BusinessValidationError("Order not found", ECode.NOTFOUND)

        # 权限检查：用户只能访问自己的订单
        if not current_user.is_admin and self.order.user_id != current_user.id:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

    def get_items(self):
        """获取订单项列表"""
        items = OrderItem.query.filter_by(order_id=self.order_id, deleted=False).all()
        return [item.to_dict() for item in items], ECode.SUCC
