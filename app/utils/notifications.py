# -*- coding: utf-8 -*-
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def notify_rider_new_order(rider_id, order_data):
    """
    向骑手发送新订单通知

    Args:
        rider_id (int): 骑手ID
        order_data (dict): 订单信息，包含订单详情
    """
    try:
        # 获取全局socketio实例
        from app import socketio

        if socketio is None:
            logger.error("SocketIO未初始化，无法发送通知")
            return False

        # 构建通知消息
        message = {
            'type': 'new_order',
            'rider_id': rider_id,
            'order': order_data,
            'timestamp': order_data.get('created_at') if order_data else None
        }

        # 发送通知到骑手通道
        socketio.emit(
            'order_notification',
            message,
            namespace='/rider/channel',
            room=f'rider_{rider_id}'  # 可选：只发送给特定骑手
        )

        logger.info(f"已向骑手 {rider_id} 发送新订单通知: {order_data.get('order_id', '未知订单')}")
        return True

    except Exception as e:
        logger.error(f"发送新订单通知失败: {e}")
        return False


def notify_order_status_update(order_id, new_status, rider_id=None):
    """
    通知订单状态更新

    Args:
        order_id (int): 订单ID
        new_status (str): 新状态
        rider_id (int, optional): 骑手ID，如果指定则只通知该骑手
    """
    try:
        from app import socketio

        if socketio is None:
            logger.error("SocketIO未初始化，无法发送通知")
            return False

        message = {
            'type': 'order_status_update',
            'order_id': order_id,
            'new_status': new_status,
            'timestamp': datetime.now().isoformat()
        }

        # 确定命名空间和房间
        namespace = '/rider/channel' if rider_id else '/restaurant/channel'
        room = f'rider_{rider_id}' if rider_id else None

        socketio.emit(
            'order_update',
            message,
            namespace=namespace,
            room=room
        )

        logger.info(f"已发送订单 {order_id} 状态更新通知: {new_status}")
        return True

    except Exception as e:
        logger.error(f"发送订单状态更新通知失败: {e}")
        return False


def notify_restaurant_new_order(restaurant_id, order_data):
    """
    向餐厅发送新订单通知

    Args:
        restaurant_id (int): 餐厅ID
        order_data (dict): 订单信息
    """
    try:
        from app import socketio

        if socketio is None:
            logger.error("SocketIO未初始化，无法发送通知")
            return False

        message = {
            'type': 'new_order',
            'restaurant_id': restaurant_id,
            'order': order_data,
            'timestamp': order_data.get('created_at') if order_data else None
        }

        socketio.emit(
            'order_notification',
            message,
            namespace='/restaurant/channel',
            room=f'restaurant_{restaurant_id}'  # 可选：只发送给特定餐厅
        )

        logger.info(f"已向餐厅 {restaurant_id} 发送新订单通知: {order_data.get('order_id', '未知订单')}")
        return True

    except Exception as e:
        logger.error(f"发送餐厅新订单通知失败: {e}")
        return False

