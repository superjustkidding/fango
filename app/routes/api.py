# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from app import jwt
from . import register_all_routes

# 创建主蓝图
main_bp = Blueprint('api', __name__)
main_api = Api(main_bp)

# 存储所有需要保护的端点
all_protected_endpoints = []


def init_app(app):
    # 初始化JWT
    jwt.init_app(app)

    # 注册用户路由并收集受保护端点
    register_all_routes(main_api, all_protected_endpoints)

    # 注册主蓝图
    app.register_blueprint(main_bp, url_prefix='/api/v1')

