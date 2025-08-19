# -*- coding: utf-8 -*-
# @Time    : 2025/8/17 0:02
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : resources.py.py
# @Software: PyCharm

from flask_restful import Resource
from flask import request
from .entities import SingleEntity, BulkEntity
from app.schemas.coupon.image_schema import ImageSchema
from app.utils.validation import validate_request
from flask_jwt_extended import jwt_required, current_user


class SingleUploadResource(Resource):
    endpoint = 'api.SingleUploadResource'

    @jwt_required()
    def post(self):
        data = validate_request(ImageSchema, request.files)
        entity = SingleEntity(current_user=current_user)
        return entity.single_upload(data)

class BulkUploadResource(Resource):
    endpoint = 'api.BulkUploadResource'

    @jwt_required()
    def post(self):
        data = validate_request(ImageSchema, request.get_json())
        entity = BulkEntity(current_user=current_user)
        return entity.bulk_upload(data)



