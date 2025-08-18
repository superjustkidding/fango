from flask import Blueprint, request, current_app
from flask_restful import Api
from .jwt import jwt
from flask_jwt_extended import verify_jwt_in_request

# 创建主蓝图
main_bp = Blueprint('api', __name__)
main_api = Api(main_bp)

# 存储所有需要保护的端点
all_protected_endpoints = []


def init_app(app):
    # 初始化JWT
    jwt.init_app(app)

    # 注册用户路由并收集受保护端点
    from .users import register_user_routes
    user_protected = register_user_routes(main_api)
    all_protected_endpoints.extend(user_protected)

    # 注册餐厅路由并收集受保护端点
    from .restaurants import register_restaurant_routes
    restaurant_protected = register_restaurant_routes(main_api)
    all_protected_endpoints.extend(restaurant_protected)

    # 注册主蓝图
    app.register_blueprint(main_bp, url_prefix='/api/v1')

    # 添加JWT保护钩子
    add_jwt_protection(app)


def add_jwt_protection(app):
    """添加JWT认证保护钩子"""

    @app.before_request
    def protect_endpoints():
        """JWT 认证保护端点"""
        # 检查当前端点是否需要保护
        if request.endpoint in all_protected_endpoints:
            try:
                verify_jwt_in_request()
            except Exception as e:
                current_app.logger.error(f"JWT verification failed: {str(e)}")
                raise
