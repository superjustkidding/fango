# -*- coding: utf-8 -*-
# @Time    : 2025/8/5 0:50
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : restaurant.py
# @Software: PyCharm

from flask import Blueprint, request, jsonify
from app import db
from app.models import Restaurant
from app.schemas import RestaurantSchema
from app.utils.validation import validate_request

restaurant_bp = Blueprint('restaurant', __name__)
schema = RestaurantSchema()

@restaurant_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_restaurant():
    data = request.validated_data
    restaurant = Restaurant(**data)
    db.session.add(restaurant)
    db.session.commit()
    return jsonify(schema.dump(restaurant)), 201

@restaurant_bp.route('/', methods=['GET'])
def get_restaurant():
    restaurant = Restaurant.query.all()
    return jsonify(schema.dump(restaurant)), 200

@restaurant_bp.route('/<int:id>', methods=['GET'])
def get_restaurants(id):
    restaurant = Restaurant.query.get_or_404(id)
    return jsonify(schema.dump(restaurant))

@restaurant_bp.route('/<int:id>/internal-users', methods=['GET'])
def get_restaurant_internaluser(id):
    restaurant = Restaurant.query.get_or_404(id)
    internal_users = restaurant.internal_users
    return jsonify(schema.dump(internal_users))


@restaurant_bp.route('/<int:id>', methods=['PUT'])
@validate_request(schema)
def update_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    data = request.validated_data
    for key, value in data.items():
        setattr(restaurant, key, value)
    db.session.commit()
    return jsonify(schema.dump(restaurant)), 200


@restaurant_bp.route('/<int:id>', methods=['DELETE'])
@validate_request(schema)
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify(schema.dump(restaurant)), 200

