# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:08
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .celery_app import celery

def init_celery(app):
    """初始化Celery并注册任务"""
    # 注册任务模块
    from . import db_tasks
    from . import email_tasks

    return celery
