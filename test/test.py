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

from app import create_app, create_socketio

app = create_app()
socketio = create_socketio(app)

def notify_rider(rider_id, message):
    socketio.emit(
        'order_notification',
        {'msg': message, 'rider_id': rider_id},
        namespace='/rider/channel'
    )


if __name__ == '__main__':
    notify_rider(1, "你有新的订单啦")
