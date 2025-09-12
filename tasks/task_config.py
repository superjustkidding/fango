# -*- coding: utf-8 -*-
# @Time    : 2025/9/12 20:39
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : start_beat_worker.py
# @Software: PyCharm


# tasks/task_config.py
import os
import yaml
from datetime import timedelta
from celery.schedules import crontab


def load_yaml_config():
    """从YAML文件加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'task_config.yml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_schedule(schedule):
    """解析调度配置"""
    if isinstance(schedule, int):
        # 如果是整数，表示秒数
        return timedelta(seconds=schedule)
    elif isinstance(schedule, str) and schedule.count(' ') == 4:
        # 如果是crontab格式的字符串
        parts = schedule.split(' ')
        return crontab(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month_of_year=parts[3],
            day_of_week=parts[4]
        )
    else:
        # 默认使用 timedelta
        return timedelta(seconds=3600)  # 1小时


class Config:
    """动态配置类"""

    def __init__(self):
        # 从 YAML 加载配置
        yaml_config = load_yaml_config()

        # 设置 Flask 配置
        flask_config = yaml_config.get('flask', {})
        self.SECRET_KEY = flask_config.get('secret_key', 'fallback-secret-key')
        self.SQLALCHEMY_DATABASE_URI = flask_config.get('sqlalchemy_database_uri', 'sqlite:///app.db')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = flask_config.get('sqlalchemy_track_modifications', False)

        # 设置 Celery 配置
        celery_config = yaml_config.get('celery', {})
        self.CELERY_BROKER_URL = celery_config.get('broker_url', 'amqp://guest:guest@localhost:5672//')
        self.CELERY_RESULT_BACKEND = celery_config.get('result_backend', 'redis://localhost:6379/0')
        self.CELERY_TIMEZONE = celery_config.get('timezone', 'Asia/Shanghai')
        self.CELERY_ENABLE_UTC = celery_config.get('enable_utc', True)

        # 设置定时任务配置
        self.CELERY_BEAT_SCHEDULE = {}
        beat_schedule = yaml_config.get('beat_schedule', {})

        for task_name, task_config in beat_schedule.items():
            self.CELERY_BEAT_SCHEDULE[task_name] = {
                'task': task_config['task'],
                'schedule': parse_schedule(task_config['schedule']),
                'args': task_config.get('args', []),
                'options': task_config.get('options', {})
            }

        # 添加其他自定义配置
        for key, value in yaml_config.items():
            if key not in ['flask', 'celery', 'beat_schedule'] and not hasattr(self, key):
                setattr(self, key, value)


# 创建配置实例
set_config = Config()
