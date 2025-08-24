# -*- coding: utf-8 -*-
# @Time    : 2025/8/23 22:16
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBHandler(logging.Handler):
    def __init__(self, mongo_uri, db_name, collection_name):
        super().__init__()
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.client.server_info()
            db = self.client[self.db_name]
            self.collection = db[self.collection_name]
            # 创建索引
            self.collection.create_index([("timestamp", 1)])
            self.collection.create_index([("level", 1)])
            self.collection.create_index([("module", 1)])
        except ConnectionFailure as e:
            print(f"MongoDB连接失败: {e}")
            self.collection = None

    def emit(self, record):
        # 修复：使用 is None 而不是真值测试
        if self.collection is None:
            self.connect()
            # 如果连接仍然失败，直接返回
            if self.collection is None:
                return

        try:
            # 在调用 format 之前设置 exc_info，这样 format 方法会自动处理异常
            if record.exc_info:
                # 确保异常信息被格式化到消息中
                record.exc_text = self.format(record)

            log_entry = {
                'timestamp': datetime.now(),
                'level': record.levelname,
                'message': self.format(record),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'pathname': record.pathname,
                'logger': record.name,
                'thread': record.thread,
                'threadName': record.threadName,
                'created': datetime.fromtimestamp(record.created)
            }

            # 添加额外字段
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id

            # 如果存在异常信息，单独存储
            if record.exc_info:
                # 使用简单的方法获取异常信息
                try:
                    # 获取异常类型和值
                    exc_type, exc_value, exc_traceback = record.exc_info
                    log_entry['exception'] = {
                        'type': str(exc_type.__name__),
                        'message': str(exc_value),
                        'traceback': self.formatException(record.exc_info) if hasattr(self, 'formatException') else str(
                            exc_value)
                    }
                except:
                    log_entry['exception'] = "无法解析异常信息"

            self.collection.insert_one(log_entry)

        except Exception as e:
            print(f"日志写入失败: {e}")

    def close(self):
        if self.client:
            self.client.close()
        super().close()
