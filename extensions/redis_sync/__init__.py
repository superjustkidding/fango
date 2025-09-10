# -*- coding: utf-8 -*-
# @Time    : 2025/8/31 0:43
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

import redis
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

# 全局Redis客户端
redis_client = None
app_instance = None

def init_redis_sync(app):
    """初始化Redis服务"""
    global redis_client, app_instance

    app_instance = app

    # 从应用配置获取Redis连接信息
    redis_host = app.config.get('REDIS_HOST', 'localhost')
    redis_port = app.config.get('REDIS_PORT', 6379)
    redis_db = app.config.get('REDIS_DB', 0)

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )

    logger.info(f"Redis service initialized with host: {redis_host}, port: {redis_port}, db: {redis_db}")

def get_redis_client():
    """获取Redis客户端实例"""
    global redis_client

    if redis_client is None:
        logger.error("Redis client not initialized. Call init_redis_sync first.")
        return None

    return redis_client

