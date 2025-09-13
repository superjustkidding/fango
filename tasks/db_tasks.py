# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 18:48
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : db_tasks.py.py
# @Software: PyCharm

# tasks/db_tasks.py
from tasks.celery_app import celery, get_redis_client
from datetime import datetime
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task
def update_coupon_status():
    """每小时更新UserCoupon状态，将不符合条件的优惠券标记为失效"""
    try:
        logger.info("开始更新优惠券状态...")

        # 延迟导入模型以避免循环依赖
        from app.models import UserCoupon, Coupon
        from app import db

        # 获取当前时间
        now = datetime.now()

        # 查找所有未使用但需要失效的优惠券
        # 条件包括：已过期、使用次数已达上限、或优惠券已被删除
        expired_coupons = db.session.query(UserCoupon).join(Coupon).filter(
            UserCoupon.status == UserCoupon.STATUS_UNUSED,
            db.or_(
                Coupon.valid_to < now,  # 已过期
                db.and_(Coupon.usage_limit.isnot(None), Coupon.usage_count >= Coupon.usage_limit),  # 使用次数已达上限
                Coupon.deleted == True  # 优惠券已被删除
            )
        ).all()

        # 更新状态为过期
        for user_coupon in expired_coupons:
            user_coupon.status = UserCoupon.STATUS_EXPIRED
            user_coupon.updated_at = now

        db.session.commit()

        logger.info(f"已更新 {len(expired_coupons)} 张失效优惠券的状态")
        return {"status": "success", "updated_count": len(expired_coupons)}

    except Exception as e:
        logger.error(f"更新优惠券状态失败: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}

@celery.task
def user_daily_coupon():
    """定时为用户发放优惠券"""
    try:
        logger.info("开始为用户发放每日优惠券...")

        # 延迟导入模型以避免循环依赖
        from app.models import UserCoupon, User, Coupon
        from app import db
        from datetime import datetime, date

        # 获取当前日期
        today = date.today()

        # 检查是否已存在今日的每日优惠券
        daily_coupon = Coupon.query.filter(
            Coupon.coupon_type == 'daily_deals',
            Coupon.valid_from <= today,
            Coupon.valid_to >= today
        ).first()

        # 如果没有今日的优惠券，则创建一个
        if not daily_coupon:
            logger.info("创建新的每日优惠券...")
            # 设置优惠券有效期（今天全天）
            valid_from = datetime.combine(today, datetime.min.time())
            valid_to = datetime.combine(today, datetime.max.time()).replace(microsecond=0)

            daily_coupon = Coupon(
                code=f"DAILY_{today.strftime('%Y%m%d')}",
                coupon_type='daily_deals',
                value=5.0,  # 默认5元优惠
                min_order_amount=20.0,  # 最低订单金额20元
                max_discount_amount=5.0,  # 最大折扣5元
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=None,  # 无使用次数限制
                usage_count=0,
                restaurant_id=None  # 通用优惠券，不限制餐厅
            )
            db.session.add(daily_coupon)
            db.session.commit()
            logger.info(f"已创建每日优惠券: {daily_coupon.code}")

        # 获取所有未删除的用户
        all_users = User.query.filter_by(deleted=False).all()
        logger.info(f"找到 {len(all_users)} 个用户需要发放优惠券")

        # 为每个用户发放优惠券
        created_count = 0
        for user in all_users:
            # 检查用户是否已经拥有今日的优惠券
            existing_coupon = UserCoupon.query.filter_by(
                user_id=user.id,
                coupon_id=daily_coupon.id,
                status=UserCoupon.STATUS_UNUSED
            ).first()

            if not existing_coupon:
                user_coupon = UserCoupon(
                    status=UserCoupon.STATUS_UNUSED,
                    used_at=None,
                    user_id=user.id,
                    coupon_id=daily_coupon.id
                )
                db.session.add(user_coupon)
                created_count += 1

        db.session.commit()
        logger.info(f"已为 {created_count} 个用户发放每日优惠券")
        return {"status": "success", "users_count": len(all_users), "coupons_created": created_count}

    except Exception as e:
        logger.error(f"发放每日优惠券失败: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}

@celery.task
def update_restaurant_sales():
    """每小时更新店铺总销售额并存储到Redis"""
    try:
        logger.info("开始更新店铺总销售额并存储到Redis...")

        # 延迟导入模型以避免循环依赖
        from app.models import Restaurant, Order
        from app import db

        # 获取Redis客户端
        redis_client = get_redis_client()

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

            # 将销售额存储到Redis，使用餐厅ID作为键
            if redis_client:
                redis_key = f"restaurant_sales:{restaurant.id}"
                redis_client.set(redis_key, str(total_sales))
            else:
                logger.warning("Redis客户端未初始化，跳过Redis存储")

            # 同时更新数据库中的销售额（可选，根据需求决定是否保留）
            # if restaurant.total_sales != total_sales:
            #     restaurant.total_sales = total_sales
                updated_count += 1

        # db.session.commit()

        logger.info(f"已更新 {updated_count} 家餐厅的销售额并存储到Redis")
        return {"status": "success", "updated_count": updated_count}

    except Exception as e:
        logger.error(f"更新店铺销售额失败: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}
