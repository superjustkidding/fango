# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:02
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : resources.py.py
# @Software: PyCharm

from flask_restful import Resource
from flask import request
from .entities import UserEntity, UserItemEntity
from app.schemas.user.user import UserCreateSchema, UserUpdateSchema, LoginSchema
from app.utils.validation import validate_request, BusinessValidationError
from app.routes.jwt import current_user, admin_required, user_required
from app.routes.logger import logger


class UserListResource(Resource):
    endpoint = 'api.UserListResource'

    @admin_required
    def get(self):
        if not current_user.is_admin:
            raise BusinessValidationError("Permission denied", 403)

        entity = UserEntity(current_user=current_user)
        logger.info("用户查询成功", entity.get_users(**request.args))
        return entity.get_users(**request.args)

    @admin_required
    def post(self):
        """创建新用户（管理员权限）"""
        data = validate_request(UserCreateSchema, request.get_json())
        entity = UserEntity(current_user=current_user)
        return entity.create_user(data)


class UserResource(Resource):
    endpoint = 'api.UserResource'

    @user_required
    def get(self, user_id):
        """获取单个用户信息"""
        entity = UserItemEntity(
            current_user=current_user,
            user_id=user_id
        )
        return entity.get_user()

    @user_required
    def put(self, user_id):
        """更新用户信息"""
        data = validate_request(UserUpdateSchema, request.get_json())
        entity = UserItemEntity(
            current_user=current_user,
            user_id=user_id
        )
        return entity.update_user(data)

    @admin_required
    def delete(self, user_id):
        """删除用户（管理员权限）"""
        entity = UserItemEntity(
            current_user=current_user,
            user_id=user_id
        )
        return entity.delete_user()


class LoginResource(Resource):
    endpoint = 'api.LoginResource'

    def post(self):
        """用户登录"""
        data = validate_request(LoginSchema, request.get_json())
        entity = UserEntity()
        return entity.login(data)

class LogoutResource(Resource):
    endpoint = 'api.LogoutResource'

    @user_required
    def delete(self, user_id):
        """删除用户（管理员权限）"""
        entity = UserItemEntity(
            current_user=current_user,
            user_id=user_id
        )
        return entity.delete_user()

class RegisterResource(Resource):
    endpoint = 'api.RegisterResource'

    def post(self):
        """用户注册"""
        data = validate_request(LoginSchema, request.get_json())
        entity = UserEntity()
        return entity.register(data)

