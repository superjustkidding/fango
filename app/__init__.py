from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import load_config

# 初始化扩展
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 加载配置
    config = load_config()
    app.config.update(config)

    # 初始化数据库
    db.init_app(app)

    # 初始化路由
    from .routes import api
    api.init_app(app)

    # 注册错误处理器
    from .utils.validation import register_error_handlers
    register_error_handlers(app)

    # 创建超级管理员（如果不存在）
    create_admin_user(app)

    return app


def create_admin_user(app):
    """创建初始管理员用户"""
    with app.app_context():
        from app.models.users.user import User
        from werkzeug.security import generate_password_hash

        admin_username = app.config.get('ADMIN_USERNAME', 'admin')
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        admin_phone = app.config.get('ADMIN_PHONE', '18000000000')

        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username=admin_username,
                email=admin_email,
                phone=admin_phone,
                password=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f"Admin user {admin_username} created")
