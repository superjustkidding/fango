# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:47
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : config.py.py
# @Software: PyCharm

from config import load_config
from datetime import timedelta
from celery.schedules import crontab


class Config:
    """动态配置类"""

    def __init__(self):
        # 从 YAML 加载配置
        yaml_config = load_config()

        # 设置 Flask 配置
        self.SECRET_KEY = yaml_config.get('SECRET_KEY', 'fallback-secret-key')
        self.SQLALCHEMY_DATABASE_URI = yaml_config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = yaml_config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)

        # 设置 Celery 配置
        self.CELERY_BROKER_URL = yaml_config.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
        self.CELERY_RESULT_BACKEND = yaml_config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
        self.CELERY_TIMEZONE = yaml_config.get('CELERY_TIMEZONE', 'Asia/Shanghai')
        self.CELERY_ENABLE_UTC = yaml_config.get('CELERY_ENABLE_UTC', True)

        # 设置定时任务配置
        self.CELERY_BEAT_SCHEDULE = {
            'cleanup-old-records': {
                'task': 'tasks.db_tasks.cleanup_old_records',
                'schedule': timedelta(hours=12),
                'args': (30,),  # 删除30天前的记录
                'options': {'queue': 'db_tasks'}
            },
            'daily-reminder': {
                'task': 'tasks.email_tasks.send_daily_reminder',
                'schedule': crontab(hour=9, minute=0),  # 每天9:00
                'options': {'queue': 'email_tasks'}
            }
        }

        # 添加其他自定义配置
        for key, value in yaml_config.items():
            if not hasattr(self, key):
                setattr(self, key, value)

# 创建配置实例
SetConfig = Config()
