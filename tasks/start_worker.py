# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:48
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : start_worker.py.py
# @Software: PyCharm


# tasks/start_worker.py
from app import create_app
from tasks import init_celery
from .config import SetConfig  # 导入配置实例

if __name__ == '__main__':
    # 创建Flask应用
    flask_app = create_app(SetConfig)

    # 初始化Celery
    celery_app = init_celery(flask_app)

    # 启动工作进程
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--queues=db_tasks,email_tasks'
    ])
