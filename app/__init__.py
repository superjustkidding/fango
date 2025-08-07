# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:54
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import load_config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    config = load_config()  # 配置
    app.config.update(config)

    db.init_app(app)   # 数据库配置
    migrate = Migrate(app, db)

    # 注册蓝图
    from .routes.api import api_bp  # 路由模式
    app.register_blueprint(api_bp, url_prefix='/api/v1')  # 版本号
    return app


