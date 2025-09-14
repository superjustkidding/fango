# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:47
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : celery_app.py
# @Software: PyCharm

from celery import Celery
from flask import Flask
from .task_config import set_config
import redis
import logging
import os

logger = logging.getLogger(__name__)

# 全局Redis客户端
redis_client = None


def init_redis():
    """初始化Redis服务"""
    global redis_client

    try:
        # 从环境变量或配置中获取Redis连接信息
        redis_url = os.environ.get('CELERY_RESULT_BACKEND', set_config.CELERY_RESULT_BACKEND)

        if redis_url.startswith('redis://'):
            # 解析Redis连接信息
            parts = redis_url.replace('redis://', '').split('/')
            host_port = parts[0].split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 6379
            db = int(parts[1]) if len(parts) > 1 else 0

            # 如果有认证信息
            if '@' in host_port[0]:
                auth, hostport = host_port[0].split('@')
                host, port = hostport.split(':') if ':' in hostport else (hostport, 6379)
                redis_client = redis.Redis(
                    host=host,
                    port=int(port),
                    db=db,
                    password=auth,
                    decode_responses=True
                )
            else:
                redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True
                )

            # 测试连接
            redis_client.ping()
            logger.info(f"Redis service initialized with host: {host}, port: {port}, db: {db}")
        else:
            logger.error(f"Unsupported result backend: {redis_url}")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}")
        redis_client = None


def get_redis_client():
    """获取Redis客户端实例"""
    global redis_client
    if redis_client is None:
        init_redis()
    return redis_client


def create_celery_app(flask_app: Flask = None):
    """创建并配置 Celery 应用"""
    if flask_app is None:
        # 创建一个简单的Flask应用，只用于提供应用上下文
        flask_app = Flask(__name__)

        # 设置数据库配置
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = set_config.SQLALCHEMY_DATABASE_URI
        flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = set_config.SQLALCHEMY_TRACK_MODIFICATIONS

        # 初始化SQLAlchemy
        from app import db
        db.init_app(flask_app)

    # 初始化Redis
    init_redis()

    celery = Celery(
        flask_app.import_name,
        broker=set_config.CELERY_BROKER_URL,
        backend=set_config.CELERY_RESULT_BACKEND,
        include=[  # 自动导入任务模块
            "tasks.db_tasks",
            "tasks.email_tasks"
        ]
    )

    # 更新配置
    celery.conf.update(
        timezone=set_config.CELERY_TIMEZONE,
        enable_utc=set_config.CELERY_ENABLE_UTC,
        beat_schedule=set_config.CELERY_BEAT_SCHEDULE,
        # 添加其他 Celery 配置
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        task_track_started=True,
        task_time_limit=30 * 60,  # 30分钟
        worker_max_tasks_per_child=100,  # 每个worker处理100个任务后重启
        worker_prefetch_multiplier=1,  # 每次预取1个任务
        # Linux 特定配置
        worker_concurrency=4,  # 使用4个进程
        worker_pool='prefork',  # 使用 prefork 池
    )

    # 设置任务上下文
    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# 全局实例，保证 `tasks.celery_app:celery` 可被 worker 找到
flask_app = Flask(__name__)
# 设置数据库配置
flask_app.config['SQLALCHEMY_DATABASE_URI'] = set_config.SQLALCHEMY_DATABASE_URI
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = set_config.SQLALCHEMY_TRACK_MODIFICATIONS

# 初始化SQLAlchemy
from app import db

db.init_app(flask_app)

celery = create_celery_app(flask_app)
