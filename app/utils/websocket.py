from flask_socketio import SocketIO, emit, join_room, leave_room

from app.utils.geo import haversine

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on("connect", namespace="/riders")
def handle_connect():
    emit("system", {"msg": "Connected"})


@socketio.on("subscribe_area", namespace="/riders")
def handle_subscribe_area(data):
    """
    管理员订阅某个区域
    data = {"lat": 31.23, "lon": 121.47, "radius": 2000}
    """
    room = f"area_{data['lat']}_{data['lon']}_{data['radius']}"
    join_room(room)
    emit("system", {"msg": f"Subscribed to {room}"})


@socketio.on("unsubscribe_area", namespace="/riders")
def handle_unsubscribe_area(data):
    room = f"area_{data['lat']}_{data['lon']}_{data['radius']}"
    leave_room(room)
    emit("system", {"msg": f"Unsubscribed from {room}"})


@socketio.on("subscribe_self", namespace="/riders")
def handle_subscribe_self(data):
    """骑手订阅自己位置上传的回执"""
    room = f"rider_{data['rider_id']}"
    join_room(room)
    emit("system", {"msg": f"Subscribed to rider {data['rider_id']}"})


def push_location_update(location_data):
    """
    推送位置更新
    location_data = {"rider_id": 1, "latitude": 31.23, "longitude": 121.47, ...}
    """
    lat, lon = location_data["latitude"], location_data["longitude"]

    # 骑手自己
    room_rider = f"rider_{location_data['rider_id']}"
    socketio.emit("rider_location_ack", location_data, namespace="/riders", room=room_rider)

    # 管理员订阅的区域
    for room in socketio.server.manager.rooms["/riders"]:
        if not room.startswith("area_"):
            continue
        _, room_lat, room_lon, room_radius = room.split("_")
        room_lat, room_lon, room_radius = float(room_lat), float(room_lon), float(room_radius)

        if haversine(lat, lon, room_lat, room_lon) <= room_radius:
            socketio.emit("rider_location_update", location_data, namespace="/riders", room=room)

