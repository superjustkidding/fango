# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:48
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : email_tasks.py.py
# @Software: PyCharm

from tasks.celery_app import celery
import time
import random
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(bind=True)
def send_welcome_email(self, user_id):
    """发送欢迎邮件（接口触发任务）"""
    try:
        logger.info(f"准备发送欢迎邮件给用户 {user_id}")

        # 延迟导入模型以避免循环依赖
        from app.models import User
        from app import db

        user = User.query.get(user_id)

        if not user:
            logger.error(f"用户 {user_id} 不存在")
            return {"status": "error", "message": "User not found"}

        # 模拟邮件发送（实际项目中替换为真实邮件发送逻辑）
        time.sleep(random.uniform(1, 3))
        logger.info(f"欢迎邮件已发送给 {user.email}")

        return {"status": "success", "email": user.email}
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        # 60秒后重试
        self.retry(exc=e, countdown=60, max_retries=3)

@celery.task
def send_daily_reminder():
    """发送每日提醒（定时任务）"""
    try:
        logger.info("开始发送每日提醒...")

        # 延迟导入模型以避免循环依赖
        from app.models import User
        from app import db

        # 获取所有用户
        users = User.query.all()

        for user in users:
            # 模拟发送过程
            time.sleep(0.5)
            logger.info(f"发送每日提醒给 {user.email}")

        logger.info(f"每日提醒发送完成! 共发送给 {len(users)} 位用户")
        return {"status": "success", "users_count": len(users)}
    except Exception as e:
        logger.error(f"发送每日提醒失败: {str(e)}")
        return {"status": "error", "message": str(e)}
