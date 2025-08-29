# -*- coding: utf-8 -*-
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)


class RiderLocationNamespace(Namespace):
    """骑手位置WebSocket处理器"""

    def on_connect(self):
        """客户端连接事件"""
        client_id = request.sid
        logger.info(f"WebSocket客户端连接: {client_id}")
        emit('connected', {
            'message': '连接成功',
            'client_id': client_id
        })

    def on_disconnect(self):
        """客户端断开连接事件"""
        client_id = request.sid
        logger.info(f"WebSocket客户端断开: {client_id}")

    def on_subscribe_rider(self, data):
        """订阅骑手位置更新"""
        try:
            rider_id = data.get('rider_id')
            if not rider_id:
                emit('error', {'message': '需要rider_id参数'})
                return

            room_name = f"rider_{rider_id}"
            join_room(room_name)

            logger.info(f"客户端 {request.sid} 订阅骑手: {rider_id}")
            emit('subscribed', {
                'rider_id': rider_id,
                'message': '订阅成功',
                'room': room_name
            })

        except Exception as e:
            logger.error(f"订阅骑手异常: {str(e)}")
            emit('error', {'message': '订阅失败'})

    def on_unsubscribe_rider(self, data):
        """取消订阅骑手"""
        try:
            rider_id = data.get('rider_id')
            if rider_id:
                room_name = f"rider_{rider_id}"
                leave_room(room_name)
                logger.info(f"客户端 {request.sid} 取消订阅骑手: {rider_id}")
                emit('unsubscribed', {'rider_id': rider_id})

        except Exception as e:
            logger.error(f"取消订阅异常: {str(e)}")

    def on_get_online_riders(self, data):
        """获取在线骑手列表"""
        try:
            # 这里可以实现获取在线骑手逻辑
            online_riders = []  # 从数据库或缓存获取

            emit('online_riders', {
                'riders': online_riders,
                'count': len(online_riders)
            })

        except Exception as e:
            logger.error(f"获取在线骑手异常: {str(e)}")
            emit('error', {'message': '获取在线骑手失败'})