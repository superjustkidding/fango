# -*- coding: utf-8 -*-
import math
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import db
from app.models import Rider, RiderLocation
from app.models.riders import rider
from app.routes.jwt import create_auth_token
from app.routes.logger import logger
from app.utils.validation import BusinessValidationError
from lib.ecode import ECode


class RiderEntity:
    def __init__(self, current_user):
        self.current_user = current_user

    def create_rider(self, data):
        if Rider.query.filter_by(name=data['name']).first():
            raise BusinessValidationError('name already exists', ECode.CONFLICT)

        if Rider.query.filter_by(email=data['email']).first():
            raise BusinessValidationError('email already exists', ECode.CONFLICT)

        rider = Rider (
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
        if not rider.check_password(data['password']):
            raise BusinessValidationError("邮箱或密码错误", ECode.AUTH)

        # 5. 更新最后登录时间
        rider.last_login = datetime.utcnow()
        db.session.commit()

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

        if 'email' in data:
            if data['email'] != self.rider.email and Rider.query.filter_by(email=data['email']).first():
                raise BusinessValidationError('email already exists', ECode.CONFLICT)
            self.rider.email = data['email']

        if 'vehicle_type' in data:
            self.rider.vehicle_type = data['vehicle_type']

        if 'license_plate' in data:
            self.rider.license_plate = data['license_plate']

        if 'delivery_radius' in data:
            if data['delivery_radius'] is not None and data['delivery_radius'] < 0:
                raise BusinessValidationError('Delivery radius cannot be negative', ECode.ERROR)
            self.rider.delivery_radius = data['delivery_radius']

            # 更新状态信息
        if 'is_online' in data:
            # 只有管理员可以强制修改在线状态
            if self.current_user.is_admin or self.current_user.id == self.rider_id:
                self.rider.is_online = data['is_online']
            else:
                raise BusinessValidationError("Only admin or rider can change online status", ECode.FORBID)

        if 'is_available' in data:
            # 只有管理员或骑手本人可以修改可用状态
            if self.current_user.is_admin or self.current_user.id == self.rider_id:
                self.rider.is_available = data['is_available']
            else:
                raise BusinessValidationError("Only admin or rider can change availability", ECode.FORBID)

        db.session.commit()
        return self.rider.to_dict(), ECode.SUCC

    def delete_rider(self):
        if not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)
        self.rider.deleted = True
        db.session.commit()
        return {'message':'deleted successfully'}, ECode.SUCC


class RiderLocationEntity:
    """骑手位置实体"""

    def __init__(self, current_user, rider_id):
        self.current_user = current_user
        self.rider_id = rider_id
        self.rider = Rider.query.filter_by(rider_id)

    def create_location(self, data):
        """创建位置记录"""
        # 权限检查：骑手只能上传自己的位置

        if not self.current_user.is_admin and self.current_user.id != self.rider_id:
            raise BusinessValidationError("权限不足", ECode.FORBID)

        # 创建位置记录
        location = RiderLocation(
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy'),
            speed=data.get('speed'),
            timestamp=data.get('timestamp', datetime.utcnow()),
            rider_id=self.rider_id
        )

        db.session.add(location)
        db.session.commit()

        # 同时更新骑手的当前位置
        rider = Rider.query.get(self.rider.id)
        if rider:
            rider.current_latitude = data['latitude']
            rider.current_longitude = data['longitude']
            rider.last_location_update = datetime.utcnow()
            db.session.commit()
        logger.info(f"骑手 {self.rider_id} 位置记录创建成功")
        return location.to_dict(), ECode.SUCC

    def get_rider_locations(self, rider_id, limit=100, start_time=None, end_time=None):
        """获取骑手位置历史"""
        # 权限检查
        if not self.current_user.is_admin and self.current_user.id != rider_id:
            raise BusinessValidationError("权限不足", ECode.FORBID)

        query = RiderLocation.query.filter_by(rider_id=rider_id)

        # 时间范围过滤
        if start_time:
            query = query.filter(RiderLocation.timestamp >= start_time)
        if end_time:
            query = query.filter(RiderLocation.timestamp <= end_time)

        # 排序和限制
        locations = query.order_by(RiderLocation.timestamp.desc()).limit(limit).all()

        return [loc.to_dict() for loc in locations], ECode.SUCC

    def get_current_location(self, rider_id):
        """获取骑手最新位置"""
        # 权限检查
        if not self.current_user.is_admin and self.current_user.id != rider_id:
            raise BusinessValidationError("权限不足", ECode.FORBID)

        try:
            location = RiderLocation.query.filter_by(rider_id=rider_id) \
                .order_by(RiderLocation.created_at.desc()) \
                .first()

            if not location:
                raise BusinessValidationError("未找到骑手位置信息", ECode.NOTFOUND)

            return location.to_dict(), ECode.SUCC

        except BusinessValidationError:
            raise
        except Exception as e:
            logger.error(f"获取最新位置失败: {str(e)}")
            raise BusinessValidationError("获取位置信息失败", ECode.ERROR)

    def get_nearby_riders(self, latitude, longitude, radius=5000, limit=20, online_only=True):
        """获取附近骑手（管理员使用）"""
        try:
            # 验证坐标
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                raise BusinessValidationError("经纬度格式错误", ECode.ERROR)

            # 计算边界框（简化版，生产环境建议使用PostGIS）
            # 1度纬度约111公里，1度经度约111*cos(latitude)公里
            lat_degree = radius / 111000
            lon_degree = radius / (111000 * math.cos(math.radians(latitude)))

            min_lat = latitude - lat_degree
            max_lat = latitude + lat_degree
            min_lon = longitude - lon_degree
            max_lon = longitude + lon_degree

            # 构建查询
            query = RiderLocation.query.filter(
                RiderLocation.latitude.between(min_lat, max_lat),
                RiderLocation.longitude.between(min_lon, max_lon),
                RiderLocation.created_at >= datetime.utcnow() - timedelta(minutes=5)  # 只查询最近5分钟的数据
            )

            if online_only:
                query = query.filter_by(online_status=True)

            # 获取每个骑手的最新位置
            subquery = db.session.query(
                RiderLocation.rider_id,
                db.func.max(RiderLocation.created_at).label('max_created_at')
            ).group_by(RiderLocation.rider_id).subquery()

            locations = query.join(
                subquery,
                db.and_(
                    RiderLocation.rider_id == subquery.c.rider_id,
                    RiderLocation.created_at == subquery.c.max_created_at
                )
            ).limit(limit).all()

            # 计算距离并排序
            riders_with_distance = []
            for loc in locations:
                distance = self._calculate_distance(latitude, longitude, loc.latitude, loc.longitude)
                if distance <= radius:
                    rider_data = loc.to_dict()
                    rider_data['distance'] = distance
                    riders_with_distance.append(rider_data)

            # 按距离排序
            riders_with_distance.sort(key=lambda x: x['distance'])

            return {
                'count': len(riders_with_distance),
                'center': {'latitude': latitude, 'longitude': longitude},
                'radius': radius,
                'riders': riders_with_distance
            }, ECode.SUCC

        except Exception as e:
            logger.error(f"获取附近骑手失败: {str(e)}")
            raise BusinessValidationError("获取附近骑手失败", ECode.ERROR)

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """计算两个坐标点之间的距离（米）"""
        # 使用Haversine公式
        R = 6371000  # 地球半径（米）

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c