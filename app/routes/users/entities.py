# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : entities.py.py
# @Software: PyCharm
import re

from app.models.users.user import User, UserAddress
from app import db
from app.utils.validation import BusinessValidationError
from werkzeug.security import generate_password_hash
from app.routes.jwt import create_auth_token
from app.routes.logger import logger
from lib.ecode import ECode


class UserEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    def get_users(self, **filters):
        # 只有管理员可以查看用户列表
        if not self.current_user or not self.current_user.is_admin:
            logger.error("Permission denied")
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        query = User.query

        # 应用过滤条件
        if 'username' in filters:
            query = query.filter(User.username.ilike(f"%{filters['username']}%"))
        if 'email' in filters:
            query = query.filter(User.email == filters['email'])

        users = query.all()
        return [u.to_dict() for u in users], ECode.SUCC

    def create_user(self, data):
        # 只有管理员可以创建用户
        if self.current_user and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            raise BusinessValidationError("Username already exists", ECode.ERROR)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            raise BusinessValidationError("Email already exists", ECode.ERROR)
        # 创建用户
        user = User(
            username = data['username'],
            email = data['email'],
            phone = data.get('phone'),
            password=generate_password_hash(data['password']),
            is_admin = data.get('is_admin', False)
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), ECode.SUCC

    def login(self, data):
        user = User.query.filter_by(username=data['username']).first()

        if not user:
            raise BusinessValidationError("Invalid username or password", ECode.AUTH)

        if not user.check_password(data['password']):
            raise BusinessValidationError("Invalid username or password", ECode.AUTH)

        # 创建访问令牌
        access_token = create_auth_token(user)

        return {
            'access_token': access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }

    def register(self, data):
        if User.query.filter_by(username=data['username']).first():
            raise BusinessValidationError("Username already exists", ECode.ERROR)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            raise BusinessValidationError("Email already exists", ECode.ERROR)
        # 创建用户
        user = User(
            username = data['username'],
            email = data['email'],
            phone = data.get('phone'),
            password=generate_password_hash(data['password']),
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), ECode.SUCC


class UserItemEntity:
    def __init__(self, current_user, user_id):
        self.current_user = current_user
        self.user_id = user_id
        self.user = User.query.get(user_id)

        if not self.user:
            raise BusinessValidationError("User not found", ECode.NOTFOUND)

    def get_user(self):
        # 用户只能查看自己的信息，管理员可以查看所有
        if self.current_user.id != self.user_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        return self.user.to_dict()

    def update_user(self, data):
        if not self.user:
            raise BusinessValidationError("User does not currently exist", ECode.ERROR)

        # 用户只能更新自己的信息，管理员可以更新所有
        if self.current_user.id != self.user_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        # 更新用户名（如果提供）
        if 'username' in data:
            # 检查新用户名是否可用
            if data['username'] != self.user.username and User.query.filter_by(username=data['username']).first():
                raise BusinessValidationError("Username already exists", ECode.ERROR)
            self.user.username = data['username']

        # 更新邮箱（如果提供）
        if 'email' in data:
            # 检查新邮箱是否可用
            if data['email'] != self.user.email and User.query.filter_by(email=data['email']).first():
                raise BusinessValidationError("Email already exists", 400)
            self.user.email = data['email']

        # 更新手机号（如果提供）
        if 'phone' in data:
            self.user.phone = data['phone']

        # 更新密码（如果提供）
        if 'password' in data:
            self.user.set_password(data['password'])

        # 更新管理员状态（只有管理员可以修改）
        if 'is_admin' in data and self.current_user.is_admin:
            self.user.is_admin = data['is_admin']

        db.session.commit()
        return self.user.to_dict(), ECode.SUCC

    def delete_user(self):
        # 只有管理员可以删除用户
        if not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", ECode.FORBID)

        # 不能删除自己
        if self.current_user.id == self.user_id:
            raise BusinessValidationError("Cannot delete your own account", ECode.ERROR)

        self.user.deleted = True
        db.session.commit()
        return {"message": "User deleted successfully"}

class UserAddressListEntity:
    def __init__(self, current_user, user_id):
        self.current_user = current_user
        self.user_id = user_id

    def create_address(self, data):

        if not self.current_user:
            raise BusinessValidationError("User does not currently exist", ECode.ERROR)

        if not data['recipient'] or not data['phone'] or not data['address'] :
            raise BusinessValidationError("收货人、电话、地址不能为空", ECode.ERROR)

        if not re.match(r"^1[3-9]\d{9}$", data['phone']):
            raise BusinessValidationError("手机号格式不正确", ECode.ERROR)

        is_default = data['is_default']
        count = UserAddress.query.filter_by(address=data['address']).count()
        if is_default:
            UserAddress.query.filter_by(
                user_id=self.user_id,
                is_default=True
            ).update({'is_default': False})
        elif count == 0:
            is_default = True
        address = UserAddress(
            user_id=self.user_id,
            label=data['label'],
            recipient=data['recipient'],
            phone=data['phone'],
            address=data['address'],
            details=data['details'],
            is_default=is_default
        )
        db.session.add(address)
        db.session.commit()
        return address.to_dict(), ECode.SUCC

    def get_address_list(self):
        if not self.current_user:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        address = UserAddress.query.filter_by(user_id=self.user_id).all()
        return [a.to_dict() for a in address], ECode.SUCC


class UserAddressEntity:
    def __init__(self, current_user, address_id):
        self.current_user = current_user
        self.address_id = address_id
        self.address = UserAddress.query.get(address_id)

    def get_address(self):

        if not self.current_user:
            raise BusinessValidationError("Permission denied", ECode.ERROR)

        address = UserAddress.query.filter_by(id=self.address_id).first()
        return address.to_dict(), ECode.SUCC

    def update_address(self, data):
        if not self.current_user:
            raise BusinessValidationError("Permission denied", ECode.ERROR)
        if not self.address:
            raise BusinessValidationError("Address does not exist", ECode.ERROR)

        if 'recipient' in data:
            self.address.recipient = data['recipient']
        if 'phone' in data:
            self.address.phone = data['phone']
        if 'address' in data:
            if data['address'] != self.address.address and UserAddress.query.filter_by(address=data['address']).first():
                raise BusinessValidationError("Address already exists", ECode.ERROR)
        if 'details' in data:
            if data['details'] != self.address.details and UserAddress.query.filter_by(details=data['details']).first():
                raise BusinessValidationError("Details already exists", ECode.ERROR)
        is_default = data['is_default']
        if is_default and not self.address.is_default:
            UserAddress.query.filter(
                UserAddress.user_id == self.current_user.id,
                UserAddress.id != self.address.id,
                UserAddress.is_default == True
            ).update({'is_default': False})
        elif is_default and self.address.is_default:
            other_default = UserAddress.query.filter(
                UserAddress.user_id == self.current_user.id,
                UserAddress.id != self.address.id,
                UserAddress.is_default == True
            ).first()
            if not other_default:
                raise BusinessValidationError("至少需要有一个默认收货地址", ECode.ERROR)
            self.address.is_default = other_default
        db.session.commit()
        return self.address.to_dict(), ECode.SUCC

    def delete_address(self):
        if not self.current_user:
            raise BusinessValidationError("Permission denied", ECode.ERROR)
        self.address.deleted = True
        db.session.commit()
        return {"message": "Address deleted successfully"}
