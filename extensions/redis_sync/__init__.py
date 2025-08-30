# -*- coding: utf-8 -*-
# @Time    : 2025/8/31 0:43
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

import redis
import json
from datetime import datetime
from app import create_app, db
from app.models import RiderLocation
import threading
import time

# 创建 Flask 应用上下文
app = create_app()


class RedisToMySQLSync:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.running = False

    def start(self):
        """启动同步服务"""
        self.running = True
        # 启动位置同步线程
        location_thread = threading.Thread(target=self.sync_locations)
        location_thread.daemon = True
        location_thread.start()

        print("Redis to MySQL sync service started")

    def stop(self):
        """停止同步服务"""
        self.running = False
        print("Redis to MySQL sync service stopped")

    def sync_locations(self):
        """同步骑手位置数据"""
        with app.app_context():
            while self.running:
                try:
                    # 从 Redis 获取最新的位置数据
                    locations = self.redis_client.zrange('rider_locations', 0, -1)

                    for location_str in locations:
                        try:
                            location_data = json.loads(location_str)

                            # 检查是否已存在数据库中
                            rider_id = location_data['rider_id']
                            timestamp = datetime.fromisoformat(location_data['timestamp'])

                            existing = RiderLocation.query.filter_by(
                                rider_id=rider_id,
                                timestamp=timestamp
                            ).first()

                            if not existing:
                                # 创建新的位置记录
                                rider_location = RiderLocation(
                                    rider_id=rider_id,
                                    latitude=location_data['latitude'],
                                    longitude=location_data['longitude'],
                                    accuracy=location_data.get('accuracy'),
                                    speed=location_data.get('speed'),
                                    timestamp=timestamp
                                )

                                db.session.add(rider_location)
                                db.session.commit()

                                # 从 Redis 中移除已处理的数据
                                self.redis_client.zrem('rider_locations', location_str)

                        except Exception as e:
                            print(f"Error processing location: {e}")

                except Exception as e:
                    print(f"Error syncing locations: {e}")

                time.sleep(5)  # 每5秒同步一次


# 创建全局同步服务实例
sync_service = RedisToMySQLSync()


def start_sync_service():
    """启动同步服务"""
    sync_service.start()


def stop_sync_service():
    """停止同步服务"""
    sync_service.stop()
