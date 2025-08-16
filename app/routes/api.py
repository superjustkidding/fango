# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:50
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : api.py
# @Software: PyCharm


from flask import Blueprint
from flask_restful import Api
from .jwt import jwt
from .user.resources import UserListResource, UserResource, LoginResource

# 创建API蓝图
blueprint = Blueprint('api', __name__)
api = Api(blueprint)


def init_app(app):
    # 初始化JWT
    jwt.init_app(app)

    # 注册用户路由
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<int:user_id>')
    api.add_resource(LoginResource, '/login')

    # 注册蓝图
    app.register_blueprint(blueprint, url_prefix='/api/v1')

    # 添加JWT认证钩子
    add_jwt_protection(app)


def add_jwt_protection(app):
    """添加JWT认证保护"""
    from flask_jwt_extended import jwt_required, verify_jwt_in_request
    from functools import wraps

    # 需要保护的端点列表
    protected_endpoints = [
        'userlistresource',
        'userresource',
        # 添加其他需要保护的端点
    ]

    @blueprint.before_request
    def protect_endpoints():
        # 检查当前端点是否需要保护
        if request.endpoint in protected_endpoints:
            try:
                verify_jwt_in_request()
            except Exception as e:
                app.logger.error(f"JWT verification failed: {str(e)}")
                raise
