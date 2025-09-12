# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:47
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : celery_app.py
# @Software: PyCharm

from celery import Celery
from flask import Flask
from .task_config import set_config   # ✅ 使用 set_config

def create_celery_app(flask_app: Flask):
    """创建并配置 Celery 应用"""
    celery = Celery(
        flask_app.import_name,
        broker=set_config.CELERY_BROKER_URL,
        backend=set_config.CELERY_RESULT_BACKEND,
        include=[                          # ✅ 自动导入任务模块
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
        worker_prefetch_multiplier=1,    # 每次预取1个任务
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
celery = create_celery_app(flask_app)


