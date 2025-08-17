# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:51
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : validation.py
# @Software: PyCharm

from functools import wraps
from flask import jsonify
from marshmallow import ValidationError


class BusinessValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_request(schema, data=None):
    """
    使用Marshmallow模式验证请求数据

    参数:
        schema: 可以是模式类或模式实例
        data: 要验证的数据（可选）

    返回:
        验证后的数据
    """
    # 如果传入的是模式类，则创建实例
    if isinstance(schema, type):
        schema = schema()

    try:
        # 如果没有提供数据，则尝试从请求中获取
        if data is None:
            from flask import request
            data = request.get_json()

        # 验证数据
        errors = schema.validate(data)
        if errors:
            raise BusinessValidationError(str(errors), 400)

        # 加载并返回验证后的数据
        return schema.load(data)
    except ValidationError as err:
        raise BusinessValidationError(str(err.messages), 400)


def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(BusinessValidationError)
    def handle_business_error(error):
        return jsonify({
            "error": "ValidationError",
            "message": error.message
        }), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "error": "NotFound",
            "message": "The requested resource was not found"
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            "error": "InternalServerError",
            "message": "An internal server error occurred"
        }), 500


# def validate_request(schema):
#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             try:
#                 data = schema.load(request.json)
#                 request.validated_data = data  # 添加验证后的数据到request对象
#             except ValidationError as err:
#                 return jsonify(err.messages), 400
#             return f(*args, **kwargs)
#         return wrapper
#     return decorator
