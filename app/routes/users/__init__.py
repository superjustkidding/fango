# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:00
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import UserListResource, UserResource, LoginResource, LogoutResource, RegisterResource, \
    UserAddressResource, UserAddressListResource, UserCouponResource


def register_user_routes(api):
    """注册用户路由到主API"""
    api.add_resource(UserListResource, '/user')  # 用户
    api.add_resource(UserResource, '/user/<int:user_id>')  # 用户详情
    api.add_resource(RegisterResource, '/user/register')  # 用户注册
    api.add_resource(LoginResource, '/user/login')   # 用户登录
    api.add_resource(LogoutResource, '/user/logout/<int:user_id>')  # 用户注销
    api.add_resource(UserAddressListResource, '/user/address/<int:user_id>')  # 配送位置增加
    api.add_resource(UserAddressResource, '/address/<int:address_id>')
    api.add_resource(UserCouponResource, '/user/coupon/<int:user_id>')  # 用户获取优惠券
    # 返回需要保护的端点列表
    return [
        'api.UserListResource',
        'api.UserResource',
        'api.LoginResource',
        'api.LogoutResource',
        'api.RegisterResource',
        'api.UserAddressResource',
        'api.UserAddressListResource',
        'api.UserCouponResource'
    ]
