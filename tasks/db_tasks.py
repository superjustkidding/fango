# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:48
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : db_tasks.py.py
# @Software: PyCharm

# tasks/db_tasks.py
from tasks.celery_app import celery
from app import db
from datetime import datetime
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# 现有的任务...
@celery.task
def update_coupon_status():
    """每小时更新UserCoupon状态，将过期的优惠券标记为过期"""
    try:
        logger.info("开始更新优惠券状态...")

        # 延迟导入模型以避免循环依赖
        from app.models import UserCoupon, Coupon

        # 获取当前时间
        now = datetime.now()

        # 查找所有未使用但已过期的优惠券
        expired_coupons = db.session.query(UserCoupon).join(Coupon).filter(
            UserCoupon.status == UserCoupon.STATUS_UNUSED,
            Coupon.expiry_date < now
        ).all()

        # 更新状态为过期
        for coupon in expired_coupons:
            coupon.status = UserCoupon.STATUS_EXPIRED
            coupon.updated_at = now

        db.session.commit()

        logger.info(f"已更新 {len(expired_coupons)} 张过期优惠券的状态")
        return {"status": "success", "updated_count": len(expired_coupons)}

    except Exception as e:
        logger.error(f"更新优惠券状态失败: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}


@celery.task
def update_restaurant_sales():
    """每小时更新店铺总销售额"""
    try:
        logger.info("开始更新店铺总销售额...")

        # 延迟导入模型以避免循环依赖
        from app.models import Restaurant, Order

        # 获取所有餐厅
        restaurants = Restaurant.query.all()

        updated_count = 0
        for restaurant in restaurants:
            # 计算该餐厅所有已完成订单的总金额
            total_sales = db.session.query(
                db.func.sum(Order.final_amount)
            ).filter(
                Order.restaurant_id == restaurant.id,
                Order.status == Order.STATUS_COMPLETED
            ).scalar() or 0.0

            # 更新餐厅总销售额
            if restaurant.total_sales != total_sales:
                restaurant.total_sales = total_sales
                updated_count += 1

        db.session.commit()

        logger.info(f"已更新 {updated_count} 家餐厅的销售额")
        return {"status": "success", "updated_count": updated_count}

    except Exception as e:
        logger.error(f"更新店铺销售额失败: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}
