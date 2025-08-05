# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:54
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import load_config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    config = load_config()
    app.config.update(config)

    db.init_app(app)

    # 注册蓝图
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
