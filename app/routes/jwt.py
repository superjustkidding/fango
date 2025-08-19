# -*- coding: utf-8 -*-

# jwt.py
from flask_jwt_extended import JWTManager
from app.models.users.user import User
from lib.ecode import ECode

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    # 确保返回字符串类型的用户ID
    return str(user.id)  # 关键修改：转换为字符串

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # 将字符串ID转换回整数查询
    return User.query.get(int(identity))  # 关键修改：转换为整数

@jwt.unauthorized_loader
def unauthorized_callback(error):
    from flask import jsonify
    return jsonify({
        "error": "Unauthorized",
        "message": "Missing or invalid access token"
    }), ECode.AUTH

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    from flask import jsonify
    return jsonify({
        "error": "TokenExpired",
        "message": "Access token has expired"
    }), ECode.AUTH

@jwt.invalid_token_loader
def invalid_token_callback(error):
    from flask import jsonify
    return jsonify({
        "error": "InvalidToken",
        "message": "Invalid access token"
    }), ECode.AUTH
