# -*- coding:utf-8 -*-
from flask_cors import CORS
from sqlalchemy.dialects.mysql import LONGTEXT
from .sqlalchemy_plus import SQLAlchemyPlus, CustomizedQuery, IdModel
from .flask_auth import JWTAuth

cross_origin_resource_sharing = CORS()

db = SQLAlchemyPlus(query_class=CustomizedQuery, model_class=IdModel)

LongText = LONGTEXT


def init_app(app):
    for extension in [cross_origin_resource_sharing, db]:
        extension.init_app(app)
