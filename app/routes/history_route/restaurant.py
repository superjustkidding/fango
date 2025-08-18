# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:50
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : restaurant.py
# @Software: PyCharm

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db

from app.schemas.restaurants.restaurant_schema import RestaurantBase


from app.models.restaurants.restaurant import Restaurant

from app.utils.validation import validate_request
from extensions.flask_auth import current_user
from lib.ecode import ECode

restaurant_bp = Blueprint('restaurant', __name__)
schema = RestaurantBase()


@restaurant_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_restaurant():
    try:
        data = request.validated_data
        # 检查邮箱是否已注册
        if Restaurant.query.filter_by(email=data['email']).first():
            return jsonify({"error": "该邮箱已注册"}), ECode.ERROR

        # 创建餐厅
        restaurant = Restaurant(**data)
        restaurant.set_password(data['password'])  # 加密密码

        db.session.add(restaurant)
        db.session.commit()

        return jsonify(schema.dump(restaurant)), ECode.SUCC

    except ValidationError as err:
        return jsonify({"error": "数据验证失败"}), ECode.ERROR


@restaurant_bp.route('/', methods=['GET'])
def get_restaurant():
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    query = Restaurant.query.filter_by(deleted=False)
    if active_only:
        query = query.filter_by(is_active=True)

    restaurants = query.order_by(Restaurant.created_at.desc()).all()
    return jsonify(schema.dump(restaurants))


@restaurant_bp.route('/<int:restaurant_id>', methods=['GET'])
def get_restaurants(restaurant_id):
    restaurant = Restaurant.query.filter_by(
        id=restaurant_id,
        deleted=False
    ).first_or_404()
    return jsonify(schema.dump(restaurant))


@restaurant_bp.route('/<int:restaurant_id>', methods=['PUT'])
@validate_request(schema)
def update_restaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(
        id=restaurant_id,
        deleted=False
    ).first_or_404()
    if current_user.id != restaurant_id :
        return jsonify({'error':'无权修改餐厅信息'}), ECode.FORBID
    try:
        data = request.validated_data
        for field in data:
            setattr(restaurant, field, data[field])
        if 'password' in data:
            restaurant.set_password(data['password'])

        db.session.commit()
        return jsonify(schema.dump(restaurant))

    except ValidationError as err:
        return jsonify({"error": "数据验证失败"}), ECode.ERROR



@restaurant_bp.route('/<int:restaurant_id>', methods=['DELETE'])
@validate_request(schema)
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify(schema.dump(restaurant)), ECode.SUCC

