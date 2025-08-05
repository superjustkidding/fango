# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:50
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : api.py
# @Software: PyCharm


from flask import Blueprint
from .restaurant import restaurant_bp
# from .user import user_bp
# from .order import order_bp
# from .product import product_bp

api_bp = Blueprint('api', __name__)

# 注册子路由 把实际的业务拆分的过程
api_bp.register_blueprint(restaurant_bp, url_prefix='/restaurants')  # 餐厅
# api_bp.register_blueprint(user_bp, url_prefix='/users')   # 用户
# api_bp.register_blueprint(order_bp, url_prefix='/orders')  # 订单
# api_bp.register_blueprint(product_bp, url_prefix='/products')  # 商品

