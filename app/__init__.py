# -*- coding: utf-8 -*-
import os
import logging
import click
import atexit

from flask import Flask, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from config import load_config
from flask_migrate import Migrate
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from extensions.logger import MongoDBHandler


# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

logger = logging.getLogger(__name__)

def setup_logging(app):
    """配置应用日志"""
    # 移除默认处理器
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # 设置日志级别
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    app.logger.setLevel(log_level)

    # 控制台处理器
    if app.config.get('LOG_TO_CONSOLE', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)

    # MongoDB处理器
    if app.config.get('LOG_TO_MONGODB', False):
        try:
            mongo_handler = MongoDBHandler(
                app.config['MONGODB_URI'],
                app.config['MONGODB_DB_NAME'],
                app.config['MONGODB_LOG_COLLECTION']
            )
            mongo_handler.setLevel(log_level)
            mongo_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            mongo_handler.setFormatter(mongo_formatter)
            app.logger.addHandler(mongo_handler)
            app.logger.info("MongoDB日志处理器初始化成功")
        except Exception as e:
            # 使用简单的 print 而不是 app.logger.error 避免循环依赖
            print(f"MongoDB日志处理器初始化失败: {e}")

    # 设置其他库的日志级别
    logging.getLogger('werkzeug').setLevel(log_level)


def create_app():
    app = Flask(__name__)

    # 加载配置
    config = load_config()
    app.config.update(config)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)

    # 配置JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # 初始化JWT
    jwt.init_app(app)

    # 初始化CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ["http://localhost:3000", "http://127.0.0.1:3000"]),
            "methods": app.config.get('CORS_METHODS', ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
            "allow_headers": app.config.get('CORS_ALLOW_HEADERS', ["Content-Type", "Authorization"]),
            "supports_credentials": app.config.get('CORS_SUPPORTS_CREDENTIALS', True)
        }
    })

    # 配置日志
    setup_logging(app)

    # 记录应用启动信息
    app.logger.info("Fango应用启动成功")
    app.logger.info(f"环境: {app.config.get('ENV', 'development')}")
    app.logger.info(f"数据库: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')}")

    # 初始化路由
    from .routes import api
    api.init_app(app)


    # 注册错误处理器
    from .utils.validation import register_error_handlers
    register_error_handlers(app)

    # 添加请求日志中间件
    @app.before_request
    def log_request_info():
        app.logger.info(
            f"请求: {request.method} {request.path}",
            extra={
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string,
                'user_id': getattr(request, 'user_id', 'anonymous'),
                'request_id': request.headers.get('X-Request-ID', 'none')
            }
        )

    @app.after_request
    def log_response_info(response):
        app.logger.info(
            f"响应: {response.status_code}",
            extra={
                'ip': request.remote_addr,
                'status_code': response.status_code,
                'user_id': getattr(request, 'user_id', 'anonymous'),
                'request_id': request.headers.get('X-Request-ID', 'none')
            }
        )
        return response

    # 创建超级管理员（如果不存在）
    @app.cli.command("create-admin")
    @with_appcontext
    def create_admin():
        """创建管理员用户"""
        from app.models.users.user import User
        from werkzeug.security import generate_password_hash

        # 使用 current_app 获取配置
        admin_username = current_app.config.get('ADMIN_USERNAME', 'admin')
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = current_app.config.get('ADMIN_PASSWORD', 'admin123')
        admin_phone = current_app.config.get('ADMIN_PHONE', '18000000000')

        # 检查是否已存在管理员
        if User.query.filter_by(is_admin=True).first():
            app.logger.info("管理员用户已存在")
            return

        # 创建新管理员
        admin = User(
            username=admin_username,
            email=admin_email,
            phone=admin_phone,
            password=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f"管理员 {admin_username} 创建成功")

    # 创建websocket通道
    # 添加自定义 CLI 命令
    @app.cli.command("run-with-websocket")
    @click.option("--host", default="0.0.0.0", help="Host to bind to")
    @click.option("--port", default=5000, help="Port to bind to")
    @click.option("--debug", is_flag=True, help="Run in debug mode")
    @with_appcontext
    def run_with_websocket(host, port, debug):
        """Run the application with WebSocket support"""
        try:
            # 导入必要的模块
            from websocket import socketio
            from extensions.redis_sync import start_sync_service, stop_sync_service

            # 初始化 SocketIO
            socketio.init_app(app)

            # 启动 Redis 同步服务
            logger.info("Starting Redis sync service...")
            start_sync_service()

            # 注册退出时的清理函数
            atexit.register(stop_sync_service)

            # 设置调试模式
            if debug:
                os.environ["DEBUG"] = "true"
                app.debug = True

            logger.info(f"Starting application with WebSocket support on {host}:{port}")
            logger.info(f"Debug mode: {debug}")

            # 使用 socketio.run 启动应用
            socketio.run(
                app,
                host=host,
                port=port,
                debug=debug,
                use_reloader=False  # 禁用重载器，避免重复启动线程
            )

        except ImportError as e:
            logger.error(f"Import error: {e}")
            logger.error("Please make sure all dependencies are installed:")
            logger.error("pip install flask-socketio eventlet redis")
            raise
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise

    return app
