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

@restaurant_bp.route('/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    return jsonify(schema.dump(restaurant))

