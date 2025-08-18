# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:08
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm


# tasks/__init__.py
from .celery_app import create_celery_app

# 全局Celery实例
celery = None


def init_celery(app):
    """初始化Celery并注册任务"""
    global celery
    if celery is None:
        celery = create_celery_app(app)

    # 注册任务模块
    from . import db_tasks
    from . import email_tasks

    return celery
