# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:47
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : celery_app.py.py
# @Software: PyCharm

# tasks/celery_app.py
from celery import Celery
from flask import Flask


def create_celery_app(flask_app: Flask):
    """创建并配置Celery应用"""
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config['CELERY_BROKER_URL'],
        backend=flask_app.config['CELERY_RESULT_BACKEND']
    )

    # 更新配置
    celery.conf.update(flask_app.config)

    # 设置任务上下文
    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

