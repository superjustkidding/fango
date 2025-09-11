# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 15:17
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : test.py
# @Software: PyCharm


# from werkzeug.security import generate_password_hash, check_password_hash
#
#
# ss = "admin123"
#
# gen = generate_password_hash(ss)
# print(gen)
#
# check_password = check_password_hash(gen, ss)
# print(check_password)
#
#
# import requests
#
# data = requests.get("http://127.0.0.1:5000/login")

from app import socketio  # 导入全局socketio实例

# 直接使用全局socketio实例发送消息
socketio.emit(
    'new_order',
    {
        'order_id': 1001,
        'message': '您有新的配送订单',
        'timestamp': '2023-11-15T10:30:00'
    },
    room='rider_123',  # 发送给特定骑手
    namespace='/rider/channel'
)

