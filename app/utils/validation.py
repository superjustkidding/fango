# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:51
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : validation.py
# @Software: PyCharm

from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError



def validate_request(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = schema.load(request.json)
                request.validated_data = data  # 添加验证后的数据到request对象
            except ValidationError as err:
                return jsonify(err.messages), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
