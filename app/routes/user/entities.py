# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : entities.py.py
# @Software: PyCharm

from app.models.users.user import User
from app import db
from app.utils.validation import BusinessValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


class UserEntity:
    def __init__(self, current_user=None):
        self.current_user = current_user

    def get_users(self, **filters):
        # 只有管理员可以查看用户列表
        if not self.current_user or not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        query = User.query

        # 应用过滤条件
        if 'username' in filters:
            query = query.filter(User.username.ilike(f"%{filters['username']}%"))
        if 'email' in filters:
            query = query.filter(User.email == filters['email'])

        users = query.all()
        return [u.to_dict() for u in users]

    def create_user(self, data):
        # 只有管理员可以创建用户
        if self.current_user and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            raise BusinessValidationError("Username already exists", 400)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            raise BusinessValidationError("Email already exists", 400)

        # 创建用户
        user = User(
            username=data['username'],
            email=data['email'],
            phone=data.get('phone'),
            is_admin=data.get('is_admin', False)
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

    def login(self, data):
        user = User.query.filter_by(username=data['username']).first()

        if not user:
            raise BusinessValidationError("Invalid username or password", 401)

        if not user.check_password(data['password']):
            raise BusinessValidationError("Invalid username or password", 401)

        # 创建访问令牌
        access_token = create_access_token(identity=user.id)

        return {
            'access_token': access_token,
            'user': user.to_dict()
        }


class UserItemEntity:
    def __init__(self, current_user, user_id):
        self.current_user = current_user
        self.user_id = user_id
        self.user = User.query.get(user_id)

        if not self.user:
            raise BusinessValidationError("User not found", 404)

    def get_user(self):
        # 用户只能查看自己的信息，管理员可以查看所有
        if self.current_user.id != self.user_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        return self.user.to_dict()

    def update_user(self, data):
        # 用户只能更新自己的信息，管理员可以更新所有
        if self.current_user.id != self.user_id and not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        # 更新用户名（如果提供）
        if 'username' in data:
            # 检查新用户名是否可用
            if data['username'] != self.user.username and User.query.filter_by(username=data['username']).first():
                raise BusinessValidationError("Username already exists", 400)
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
        return self.user.to_dict()

    def delete_user(self):
        # 只有管理员可以删除用户
        if not self.current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        # 不能删除自己
        if self.current_user.id == self.user_id:
            raise BusinessValidationError("Cannot delete your own account", 400)

        db.session.delete(self.user)
        db.session.commit()
        return {"message": "User deleted successfully"}