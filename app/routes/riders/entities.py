# -*- coding: utf-8 -*-
import math
from datetime import datetime, timedelta, timezone
import socketio
from flask import json
from werkzeug.security import generate_password_hash
from app import db
from app.models import Rider, RiderLocation, RiderAssignment
from app.routes.jwt import create_auth_token
from app.utils.geo import haversine
from app.utils.validation import BusinessValidationError
from app.utils.websocket import  redis_client, TASK_ASSIGNMENT_CHANNEL
from lib.ecode import ECode


class RiderEntity:
    def __init__(self, current_user):
        self.current_user = current_user

    def create_rider(self, data):
        if Rider.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        if Rider.query.filter_by(email=data['email']).first():
            raise BusinessValidationError('email already exists', ECode.CONFLICT)

        rider = Rider(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            password_hash=generate_password_hash(data['password_hash']),
            avatar=data['avatar'],
            vehicle_type=data['vehicle_type'],
            license_plate=data['license_plate'],
            is_available=data.get('is_available', True),
            is_online=data.get('is_online', True)
         )
        db.session.add(rider)
        db.session.commit()
        return rider.to_dict(), ECode.SUCC

    """获取全部骑手（仅管理员）"""

    def get_all_riders(self, **filters):
        # 权限检查 - 只有管理员可以访问
        if not self.current_user or not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        query = Rider.query.filter_by(deleted=False)

        # 应用过滤器
        if 'is_online' in filters:
            query = query.filter(Rider.is_online == filters['is_online'])

        if 'is_available' in filters:
            query = query.filter(Rider.is_available == filters['is_available'])

        if 'name' in filters and filters['name']:
            query = query.filter(Rider.name.ilike(f"%{filters['name']}%"))

        if 'phone' in filters and filters['phone']:
            query = query.filter(Rider.phone.ilike(f"%{filters['phone']}%"))

        # 排序
        query = query.order_by(Rider.created_at.desc())

        riders = query.all()
        return [r.to_dict() for r in riders], ECode.SUCC

    def rider_login(self, data):
        # 1. 根据邮箱查询骑手（排除已删除的）
        rider = Rider.query.filter_by(email=data['email'], deleted=False).first()

        # 2. 验证骑手存在性
        if not rider:
            raise BusinessValidationError("邮箱或密码错误", ECode.AUTH)

        # 3. 检查账户状态
        if not rider.is_active:
            raise BusinessValidationError("账户已被禁用", ECode.FORBID)

        # 4. 验证密码
        if not rider.check_password(data['password_hash']):
            raise BusinessValidationError("邮箱或密码错误", ECode.AUTH)

        # 6. 创建访问令牌
        access_token = create_auth_token(rider)

        # 7. 返回完整的登录结果
        return {
            'access_token': access_token,
            'rider': {
                'id': rider.id,
                'name': rider.name,
                'email': rider.email,
                'phone': rider.phone,
                'is_online': rider.is_online,
                'is_available': rider.is_available,
            }
        }, ECode.SUCC

    def rider_logout(self):
        rider = Rider.query.get(self.current_user.id)
        if not rider:
            raise BusinessValidationError('Rider not found', ECode.FORBID)

        rider.is_online = False
        rider.is_available = False
        rider.last_login = datetime.now(timezone.utc)
        db.session.commit()
        return {'msg':'logout successfully'}, ECode.SUCC

    def start_taking_orders(self):
        rider = Rider.query.get(self.current_user.id)
        if not rider:
            raise BusinessValidationError('Rider not found', ECode.FORBID)
        rider.is_online = True
        rider.is_available = True
        db.session.commit()
        return rider.to_dict(), ECode.SUCC

    def stop_taking_orders(self):
        rider = Rider.query.get(self.current_user.id)
        if not rider:
            raise BusinessValidationError('Rider not found', ECode.FORBID)
        rider.is_available = False
        db.session.commit()
        return rider.to_dict(), ECode.SUCC


class RiderItemEntity:
    def __init__(self, current_user, rider_id):
        self.current_user = current_user
        self.rider_id = rider_id
        self.rider = Rider.query.filter_by(id=rider_id).first()

        if not self.rider:
            raise BusinessValidationError("Rider not found", ECode.NOTFOUND)

    def get_rider(self):
        if self.current_user.id != self.rider.id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        return self.rider.to_dict(), ECode.SUCC

    def update_rider(self, data):
        if self.current_user.id != self.rider.id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        if 'name' in data:
            if data['name'] != self.rider.name and Rider.query.filter_by(name=data['name']).first():
                raise BusinessValidationError('name already exists', ECode.CONFLICT)
            self.rider.name = data['name']

        if 'phone' in data:
            self.rider.phone = data['phone']

        if 'password_hash' in data:

            self.rider.password_hash = generate_password_hash(data['password'])

        if 'vehicle_type' in data:
            self.rider.vehicle_type = data['vehicle_type']

        if 'license_plate' in data:
            self.rider.license_plate = data['license_plate']

        db.session.commit()
        return self.rider.to_dict(), ECode.SUCC

    def delete_rider(self):
        if not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        self.rider.deleted = True
        db.session.commit()
        return {'message': 'deleted successfully'}, ECode.SUCC


class RiderLocationEntity:
    def __init__(self, current_user, rider_id):
        self.current_user = current_user
        self.rider_id = rider_id
        self.rider = Rider.query.filter_by(id=rider_id).first()
        if not self.rider:
            raise BusinessValidationError("Rider not found", ECode.NOTFOUND)

    def get_location_history(self, limit=50, order_id=None):
        """获取骑手历史位置"""
        key = f"rider_locations:{self.rider_id}"
        if order_id:
            history = redis_client.zrevrange(key, 0, limit - 1)
            if history:
                filtered =[
                    json.loads(h) for h in history
                    if json.loads(h).get("order_id") == order_id

                ]
                if filtered:
                    return filtered[:limit], ECode.SUCC

            history_db = (
                RiderLocation.query.filter_by(rider_id=self.rider_id)
                .order_by(RiderLocation.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [loc.to_dict() for loc in history_db], ECode.SUCC
        return None






