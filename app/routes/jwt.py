# -*- coding: utf-8 -*-
# @Time    : 2025/8/20 22:52
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : jwt.py
# @Software: PyCharm


# 创建身份验证工具函数

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from flask import jsonify, current_app
from datetime import timedelta
from functools import wraps
import json
from werkzeug.local import LocalProxy

# 从应用包中导入 jwt 实例和模型
from app import jwt
from app.models.users.user import User
from app.models.restaurants.restaurant import Restaurant
from app.models.riders.rider import Rider


def create_auth_token(identity_obj):
    """创建认证令牌"""
    # 根据身份类型设置不同的令牌内容和过期时间
    token_data = {
        'id': identity_obj.id,
        'type': None,
        'is_admin': False
    }

    # 用户类型处理
    if hasattr(identity_obj, 'is_admin') and identity_obj.is_admin:
        token_data['type'] = 'admin'
        token_data['is_admin'] = True
        expires_delta = timedelta(hours=8)  # 管理员令牌有效期较短
    elif hasattr(identity_obj, 'user_type'):
        token_data['type'] = identity_obj.user_type
        expires_delta = timedelta(hours=24)
    else:
        # 默认处理
        if hasattr(identity_obj, '__tablename__'):
            if identity_obj.__tablename__ == 'users':
                token_data['type'] = 'user'
            elif identity_obj.__tablename__ == 'restaurants':
                token_data['type'] = 'restaurant'
            elif identity_obj.__tablename__ == 'riders':
                token_data['type'] = 'rider'
        expires_delta = timedelta(hours=24)

    # 将身份数据转换为 JSON 字符串作为 identity
    identity_str = json.dumps(token_data)

    access_token = create_access_token(
        identity=identity_str,  # 使用字符串而不是字典
        expires_delta=expires_delta
    )

    return access_token


def get_current_identity():
    """获取当前身份信息"""
    identity_str = get_jwt_identity()
    try:
        # 将字符串解析回字典
        return json.loads(identity_str)
    except (json.JSONDecodeError, TypeError):
        # 如果无法解析，返回原始字符串
        return {'id': identity_str, 'type': 'unknown', 'is_admin': False}


def get_current_user():
    """获取当前用户对象"""
    try:
        # 获取身份信息
        identity = get_current_identity()
        identity_type = identity.get('type')
        identity_id = identity.get('id')

        # 根据类型加载不同的对象
        if identity_type == 'user' or identity_type == 'admin':
            return User.query.get(identity_id)
        elif identity_type == 'restaurant':
            return Restaurant.query.get(identity_id)
        elif identity_type == 'rider':
            return Rider.query.get(identity_id)
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {e}")

    return None


# 创建 LocalProxy
current_user = LocalProxy(get_current_user)


# 自定义JWT声明回调
@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    """添加自定义声明到JWT令牌"""
    try:
        # 尝试解析身份信息
        identity_data = json.loads(identity)
        return {
            'identity_type': identity_data.get('type'),
            'is_admin': identity_data.get('is_admin', False)
        }
    except (json.JSONDecodeError, TypeError):
        # 如果无法解析，返回默认声明
        return {
            'identity_type': 'unknown',
            'is_admin': False
        }


# JWT错误处理
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    # 这些错误处理函数可以返回 Response 对象，因为它们直接由 Flask 处理
    return jsonify({
        "msg": "缺少访问令牌",
        "error": "missing_jwt"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return jsonify({
        "msg": "无效的访问令牌",
        "error": "invalid_jwt"
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "msg": "访问令牌已过期",
        "error": "expired_jwt"
    }), 401


# 权限装饰器 - 返回字典而不是 Response 对象
def require_role(role_name):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_identity = get_current_identity()

            # 管理员可以访问所有接口
            if current_identity.get('is_admin'):
                return fn(*args, **kwargs)

            # 检查特定角色
            if role_name == 'any':
                return fn(*args, **kwargs)

            if current_identity.get('type') != role_name:
                # 返回字典而不是 jsonify() 的结果
                return {"msg": "权限不足"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


# 特定角色的装饰器
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not is_admin():
            # 返回字典而不是 jsonify() 的结果
            return {"msg": "需要管理员权限"}, 403
        return fn(*args, **kwargs)

    return wrapper


def user_required(fn):
    return require_role('user')(fn)


def restaurant_required(fn):
    return require_role('restaurant')(fn)


def rider_required(fn):
    return require_role('rider')(fn)


def is_admin():
    """检查当前身份是否是管理员"""
    identity = get_current_identity()
    return identity.get('is_admin', False)


def get_identity_type():
    """获取当前身份类型"""
    identity = get_current_identity()
    return identity.get('type')


def get_identity_id():
    """获取当前身份ID"""
    identity = get_current_identity()
    return identity.get('id')

