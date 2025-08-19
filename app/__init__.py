# -*- coding: utf-8 -*-

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from config import load_config
from flask_migrate import Migrate
from datetime import timedelta

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # 加载配置
    config = load_config()
    app.config.update(config)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=15)  # 访问令牌1小时过期
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # 刷新令牌30天过期

    # 初始化JWT
    from .routes.jwt import jwt
    jwt.init_app(app)

    # 初始化路由
    from .routes import api
    api.init_app(app)

    # 注册错误处理器
    from .utils.validation import register_error_handlers
    register_error_handlers(app)

    # 创建超级管理员（如果不存在）
    # 注册 CLI 命令
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
            print("管理员用户已存在")
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
        print(f"管理员 {admin_username} 创建成功")

    return app

