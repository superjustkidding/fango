# -*- coding: utf-8 -*-
# @Time    : 2025/8/19 15:01
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : image_schema.py
# @Software: PyCharm


from marshmallow import Schema, fields

class ImageSchema(Schema):
    original_name = fields.Str(required=True)
    stored_name = fields.Str(required=True)
    file_path = fields.Str(required=True)
    url = fields.Str(required=True)
