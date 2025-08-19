# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:00
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import UserListResource, UserResource, LoginResource


def register_user_routes(api):
    """注册用户路由到主API"""
    api.add_resource(UserListResource, '/users')  # 用户
    api.add_resource(UserResource, '/users/<int:user_id>')  # 用户详情
    api.add_resource(LoginResource, '/login')  # 用户登录

    # 返回需要保护的端点列表
    return [
        'api.UserListResource',
        'api.UserResource',
        'api.LoginResource',
    ]
