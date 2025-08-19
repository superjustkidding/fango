# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:00
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : __init__.py.py
# @Software: PyCharm

from .resources import SingleUploadResource, BulkUploadResource


def register_user_routes(api):
    """注册用户路由到主API"""
    api.add_resource(SingleUploadResource, '/single/upload')  # 单个文件上传
    api.add_resource(BulkUploadResource, '/bulk/upload')  # 批量文件上传

    return [
        'api.SingleUploadResource',
        'api.BulkUploadResource',
    ]
