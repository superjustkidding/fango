# -*- coding: utf-8 -*-
# @Time    : 2025/9/12 20:39
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : start_beat_worker.py
# @Software: PyCharm

import os
import sys
import subprocess
import platform

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tasks import init_celery

def get_runtime_dir():
    """获取 Celery 运行时文件存储目录"""
    tasks_dir = os.path.dirname(os.path.abspath(__file__))
    runtime_dir = os.path.join(tasks_dir, "runtime")

    # 如果不存在则自动创建
    if not os.path.exists(runtime_dir):
        os.makedirs(runtime_dir, exist_ok=True)

    return runtime_dir

def start_celery_worker():
    """启动 Celery worker"""
    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'tasks.celery_app:celery',
        'worker',
        '--loglevel=info',
        '--queues=db_tasks,email_tasks',
        '--hostname=worker@%h'
    ]

    # Windows 下强制使用 solo 模式，避免 billiard 多进程问题
    if platform.system().lower().startswith("win"):
        cmd.append('--pool=solo')
    else:
        # Linux/Unix 可以安全使用并发
        cmd.append('--concurrency=4')

    return subprocess.Popen(cmd)

def start_celery_beat():
    """启动 Celery beat"""
    runtime_dir = get_runtime_dir()

    pidfile_path = os.path.join(runtime_dir, 'celery_beat.pid')
    logfile_path = os.path.join(runtime_dir, 'celery_beat.log')
    scheduler_path = os.path.join(runtime_dir, 'celery_beat_schedule')

    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'tasks.celery_app:celery',
        'beat',
        '--loglevel=info',
        f'--pidfile={pidfile_path}',
        f'--logfile={logfile_path}',
        f'--schedule={scheduler_path}'
    ]
    return subprocess.Popen(cmd)

if __name__ == '__main__':
    try:
        # 初始化 Celery
        celery_app = init_celery(None)

        print("启动 Celery worker 和 beat...")

        # 启动 worker 和 beat
        worker_process = start_celery_worker()
        beat_process = start_celery_beat()

        # 等待进程结束
        worker_process.wait()
        beat_process.wait()

    except KeyboardInterrupt:
        print("接收到中断信号，正在停止进程...")
        if 'worker_process' in locals():
            worker_process.terminate()
        if 'beat_process' in locals():
            beat_process.terminate()

        if 'worker_process' in locals():
            worker_process.wait()
        if 'beat_process' in locals():
            beat_process.wait()

        print("所有进程已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)