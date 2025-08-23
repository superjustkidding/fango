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

    def emit(self, record):
        if not self.collection:
            self.connect()

        try:
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

            if record.exc_info:
                log_entry['exc_info'] = self.formatException(record.exc_info)

            self.collection.insert_one(log_entry)

        except Exception as e:
            print(f"日志写入失败: {e}")

    def close(self):
        if self.client:
            self.client.close()
        super().close()
