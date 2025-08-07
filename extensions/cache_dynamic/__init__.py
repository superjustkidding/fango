# -*- coding:utf-8 -*-

import hashlib
from flask import request
from extensions.flask_auth import current_user


def make_cache_key(*args, **kwargs):
    """Dynamic creation the request url."""
    path = request.path
    parameter_data = 0
    if request.query_string:
        parameter_data = hashlib.md5(request.query_string).hexdigest()
    json_data = 0
    if request.json:
        json_data = hashlib.md5(str(request.json).encode('utf-8')).hexdigest()
    unit_id = current_user.unit_id
    admin_role = current_user.admin_role
    account_type = current_user.unit_type
    cache_path = "{0}{1}/{2}/{3}/{4}/{5}".format(path, unit_id, admin_role,
                                                 account_type, parameter_data, json_data)
    return str(cache_path.encode('utf-8'))
