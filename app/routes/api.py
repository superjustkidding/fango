# -*- coding: utf-8 -*-

from flask import Blueprint, request
from flask_restful import Api
from app import jwt
from . import register_all_routes
import logging

# 创建主蓝图
main_bp = Blueprint('api', __name__)
main_api = Api(main_bp)

# 存储所有需要保护的端点
all_protected_endpoints = []

# 创建日志记录器
logger = logging.getLogger(__name__)


def init_app(app):
    # 初始化JWT
    jwt.init_app(app)

    # 注册用户路由并收集受保护端点
    register_all_routes(main_api, all_protected_endpoints)

    # 注册主蓝图
    app.register_blueprint(main_bp, url_prefix='/api/v1')

    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        logger.info('健康检查请求')
        return {
            'status': 'healthy',
            'services': {
                'database': 'connected',
                'mongodb': 'connected' if app.config.get('LOG_TO_MONGODB') else 'disabled'
            }
        }

    # 添加日志测试端点
    @app.route('/api/test-log')
    def test_log():
        """测试日志记录"""
        logger.debug('这是一条调试日志')
        logger.info('这是一条信息日志')
        logger.warning('这是一条警告日志')
        logger.error('这是一条错误日志')

        try:
            # 故意制造异常
            raise ValueError('这是一个测试异常')
        except Exception as e:
            logger.exception('捕获到异常')

        return {'message': '日志测试完成'}

