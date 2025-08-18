# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:49
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : start_beat.py.py
# @Software: PyCharm

# tasks/start_beat.py
from app import create_app
from tasks import init_celery
from .config import SetConfig   # 导入配置实例

if __name__ == '__main__':
    # 创建Flask应用
    flask_app = create_app(SetConfig)

    # 初始化Celery
    celery_app = init_celery(flask_app)

    # 启动定时任务调度器
    celery_app.Beat().run()
