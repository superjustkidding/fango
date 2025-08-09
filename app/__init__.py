# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 17:54
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py
# @Software: PyCharm
from datetime import timedelta

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from .config import load_config

# 创建数据库实例
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    config = load_config()
    app.config.update(config)

    # 初始化数据库
    db.init_app(app)

    # 确保所有模型被导入
    with app.app_context():
        # 导入所有模型
        from .models import users, orders, coupon

        # 反射数据库元数据
        db.reflect()

    # 注册蓝图
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # 将 db 附加到 app 实例
    app.db = db

    return app
