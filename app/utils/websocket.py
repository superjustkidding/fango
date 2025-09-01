# -*- coding: utf-8 -*-

import redis
import json
from app import db
from app.models import Rider
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.utils.geo import haversine


# 初始化 Redis 连接
redis_client = redis.Redis(host='localhost',
                           port=6379,
                           db=0,
                           decode_responses=True)

socketio = SocketIO(cors_allowed_origins="*")

# 骑手位置更新通道名称
RIDER_LOCATION_CHANNEL = "rider_locations"
# 任务分配通道名称
TASK_ASSIGNMENT_CHANNEL = "task_assignments"




@socketio.on("connect", namespace="/riders")
def handle_connect():
    emit("system", {"msg": "Connected"})


@socketio.on("rider_connect", namespace="/riders")
def handle_rider_connect(data):
    """骑手连接并认证"""
    rider_id = data.get('rider_id')
    token = data.get('token')
    # token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1NTczNTk1MSwianRpIjoiNDNlZWU1MGMtOWY0ZC00YmNjLTlmZmUtNTQxNjgxNjE5MGRhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IntcImlkXCI6IDEsIFwidHlwZVwiOiBcInJlc3RhdXJhbnRcIiwgXCJpc19hZG1pblwiOiBmYWxzZX0iLCJuYmYiOjE3NTU3MzU5NTEsImNzcmYiOiIyMjdmOThkOS0zZmI5LTRjZGQtOWZhNS05NDFjY2I1NTU3NmUiLCJleHAiOjE3NTU4MjIzNTEsImlkZW50aXR5X3R5cGUiOiJyZXN0YXVyYW50IiwiaXNfYWRtaW4iOmZhbHNlfQ.uBgERbLMMV9eCltTm6MzBKEKKdJjSV26gMgv4YecxyQ "
    # token = {"rider_id":1, "order_uuid":"xxxxxxxxxxxxxxxx"}

    # 这里应该添加认证逻辑，验证 token 和 rider_id 的有效性
    # 简化示例，假设认证通过

    # 骑手加入自己的房间
    room = f"rider_{rider_id}"
    join_room(room)

    # 更新骑手在线状态
    rider = Rider.query.get(rider_id)
    if rider:
        rider.is_online = True
        db.session.commit()

    emit("system", {"msg": f"Rider {rider_id} connected"})


@socketio.on("rider_disconnect", namespace="/riders")
def handle_rider_disconnect(data):
    """骑手断开连接"""
    rider_id = data.get('rider_id')

    # 更新骑手在线状态
    rider = Rider.query.get(rider_id)
    if rider:
        rider.is_online = False
        db.session.commit()

    emit("system", {"msg": f"Rider {rider_id} disconnected"})


@socketio.on("rider_location_update", namespace="/riders")
def handle_rider_location_update(data):
    """接收骑手位置更新"""
    rider_id = data.get('rider_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    speed = data.get('speed')

    # 将位置数据存入 Redis
    location_data = {
        'rider_id': rider_id,
        'latitude': latitude,
        'longitude': longitude,
        'accuracy': accuracy,
        'speed': speed,
        'timestamp': datetime.utcnow().isoformat()
    }

    # 发布到 Redis 频道
    redis_client.publish(RIDER_LOCATION_CHANNEL, json.dumps(location_data))

    # 同时存入 Redis 有序集合，用于最近位置查询
    redis_client.zadd(
        'rider_locations',
        {f"{rider_id}_{datetime.utcnow().timestamp()}": json.dumps(location_data)}
    )

    # 保留最近 100 个位置
    redis_client.zremrangebyrank('rider_locations', 0, -101)

    emit("location_ack", {"status": "success", "msg": "Location updated"})


def assign_task_to_rider(task_data):
    """分配任务给骑手"""
    rider_id = task_data.get('rider_id')
    task_id = task_data.get('task_id')

    # 发布任务到 Redis
    redis_client.publish(TASK_ASSIGNMENT_CHANNEL, json.dumps(task_data))

    # 同时通过 WebSocket 通知骑手
    room = f"rider_{rider_id}"
    socketio.emit("task_assigned", task_data, namespace="/riders", room=room)

