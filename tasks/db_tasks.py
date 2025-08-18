# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:48
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : db_tasks.py.py
# @Software: PyCharm


# tasks/db_tasks.py
from . import celery  # 从全局导入celery实例
from app import db
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(bind=True)
def cleanup_old_records(self, days=30):
    """清理旧记录（定时任务）"""
    try:
        logger.info(f"开始清理超过 {days} 天的旧记录...")

        # 延迟导入模型以避免循环依赖
        from app.models import ActivityLog

        threshold = datetime.utcnow() - timedelta(days=days)

        # 执行清理操作
        deleted_count = db.session.query(ActivityLog).filter(
            ActivityLog.timestamp < threshold
        ).delete()
        db.session.commit()

        logger.info(f"清理完成! 删除了 {deleted_count} 条记录")
        return {"deleted_records": deleted_count}
    except Exception as e:
        logger.error(f"清理失败: {str(e)}")
        # 30秒后重试
        self.retry(exc=e, countdown=30, max_retries=3)


@celery.task
def log_user_activity(user_id, action, details=None):
    """记录用户活动（接口触发任务）"""
    try:
        logger.info(f"记录用户活动: user_id={user_id}, action={action}")

        # 延迟导入模型以避免循环依赖
        from app.models import ActivityLog

        # 创建日志记录
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details or {}
        )

        db.session.add(activity)
        db.session.commit()

        return {"status": "success", "activity_id": activity.id}
    except Exception as e:
        logger.error(f"记录活动失败: {str(e)}")
        return {"status": "error", "message": str(e)}
