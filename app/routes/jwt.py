# -*- coding:utf-8 -*-
from flask_jwt_extended import JWTManager
from app.models.users.user import User
from lib.ecode import ECode

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

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
