# -*- coding:utf-8 -*-
from flask_restful import Resource
from .decorator import response_json


class CommonResource(Resource):
    method_decorators = [response_json()]
