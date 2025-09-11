# -*- coding: utf-8 -*-
from datetime import datetime

from app import db
from app.models import Coupon, UserCoupon, User
from app.routes.logger import logger
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode


class CouponEntity:
    def __init__(self, current_user):
        self.current_user = current_user

    def create_coupon(self, data):
        if Coupon.query.filter_by(code=data['code']).first():
            logger.warning('Coupon code already exists: %s', data['code'])
            raise BusinessValidationError("Coupon code already exists", ECode.CONFLICT)
        if data['valid_to'] <= data['valid_from']:
            raise BusinessValidationError("Coupon valid_to must be greater than valid from", ECode.ERROR)
        coupon = Coupon(
            code=data['code'],
            coupon_type=data['coupon_type'],
            value=data['value'],
            min_order_amount=data.get('min_order_amount', 0.0),
            max_discount_amount=data.get('max_discount_amount'),
            valid_from=data['valid_from'],
            valid_to=data['valid_to'],
            usage_limit=data['usage_limit']
        )
        db.session.add(coupon)
        db.session.commit()
        logger.info('Coupon created: %s', coupon.id)
        return coupon.to_dict(), ECode.SUCC

    def get_all_coupons(self, **filters):
        if not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        query = Coupon.query.filter_by(deleted=False)
        if 'coupon_type' in filters:
            query = query.filter(Coupon.coupon_type.ilike(f"%{filters['coupon_type']}%"))
        coupons = query.all()
        return [c.to_dict() for c in coupons], ECode.SUCC


class CouponAssignEntity:
    def __init__(self, coupon_id):
        self.coupon_id = coupon_id
        self.coupon = Coupon.query.get(coupon_id)
        if not self.coupon:
            raise BusinessValidationError("Coupon does not exist", ECode.CONFLICT)

    def assign_user_single(self, user_id):
        """管理员发放给单个的用户优惠券"""
        user = User.query.get(user_id)
        if not user:
            raise BusinessValidationError("User does not exist", ECode.CONFLICT)
        existing = UserCoupon.query.filter_by(user_id=user_id, coupon_id=self.coupon_id).first()
        if existing:
            logger.warning('Coupon already exists: %s', existing.coupon_id)
            raise BusinessValidationError("Coupon already assigned", ECode.CONFLICT)

        user_coupon = UserCoupon(user_id=user_id, coupon_id=self.coupon_id)
        db.session.add(user_coupon)
        db.session.commit()
        return user_coupon.to_dict(), ECode.SUCC

    def auto_assign_coupon(self):
        """自动发放优惠券给所有用户"""
        users = User.query.all()
        if not users:
            raise BusinessValidationError("No users found", ECode.CONFLICT)

        assigned, skipped = [], []

        for user in users:
            if UserCoupon.query.filter_by(user_id=user.id, coupon_id=self.coupon_id).first():
                skipped.append(user.id)
                continue

            uc = UserCoupon(user_id=user.id, coupon_id=self.coupon_id)
            db.session.add(uc)
            assigned.append(user.id)

        db.session.commit()

        logger.info("Coupon %s auto-assigned. Success: %s, Skipped: %s",
                    self.coupon_id, assigned, skipped)

        return {
                "coupon": self.coupon.to_dict(),
                "assigned_users": assigned,
                "skipped_users": skipped
            }, ECode.SUCC

class CouponListEntity:
    def __init__(self, coupon_id):
        self.coupon_id = coupon_id
        self.coupon = Coupon.query.get(coupon_id)
        if not self.coupon:
            logger.warning("Coupon not found: %s", coupon_id)
            raise BusinessValidationError("Coupon does not exist", ECode.CONFLICT)

    def delete_coupon(self):
        self.coupon.deleted = True
        db.session.commit()
        return {'msg': 'Coupon deleted'}, ECode.SUCC

    def update_coupon(self, data):
        if 'coupon_type' in data:
            if data['coupon_type'] not in ['percentage', 'fixed']:
                raise BusinessValidationError("Invalid coupon type", ECode.FORBID)
            self.coupon.coupon_type = data['coupon_type']
        if 'value' in data:
            self.coupon.value = float(data['value'])
        if 'min_order_amount' in data:
            self.coupon.min_order_amount = float(data['min_order_amount'])
        if 'max_discount_amount' in data:
            self.coupon.max_discount_amount = float(data['max_discount_amount'])
        print(f"Received data types:")
        for key, value in data.items():
            print(f"  {key}: {type(value)} = {value}")

        # # 处理valid_from
        # if 'valid_from' in data:
        #     print(f"valid_from type: {type(data['valid_from'])}")
        #     print(f"valid_from value: {data['valid_from']}")
        #     self.coupon.valid_from = datetime.fromisoformat(data["valid_from"])
        if 'valid_from' in data:
            self.coupon.valid_from = data["valid_from"]
        if 'valid_to' in data:
            self.coupon.valid_to = data["valid_to"]
        if 'usage_limit' in data:
            self.coupon.usage_limit = data['usage_limit']
        db.session.commit()
        logger.info('Coupon %s updated', self.coupon_id)
        return self.coupon.to_dict(), ECode.SUCC













