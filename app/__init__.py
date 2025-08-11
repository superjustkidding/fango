import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import load_config

from werkzeug.security import generate_password_hash

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    config = load_config()
    app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)  # 这里初始化 Flask-Migrate

    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    with app.app_context():
        from .models import (
            basemodel,
            users,
            coupon,
            orders,
            restaurants,
            rider,
            payment
        )

        from app.models.users.user import User  # 延迟导入，防止循环依赖
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        phone = os.getenv("ADMIN_PHONE", 18000000000)

        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                phone= phone,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f"超级管理员 {username} 已创建")
        else:
            app.logger.info("超级管理员已存在")

    return app
