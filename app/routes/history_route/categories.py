# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.restaurants.restaurant import Restaurant, MenuItem, MenuCategory
from app.schemas.schemas import MenuItemSchema, OrderSchema
from app.utils.validation import validate_request
from lib.ecode import ECode

category_bp = Blueprint('categories', __name__)
schema = MenuItemSchema()


# 获取所有商品分类
@category_bp.route('/', methods=['GET'])
def get_all_categories():

    restaurant_id = request.args.get('restaurant_id')
    include_inactive = request.args.get('is_active', 'false').lower() == 'true'

    query = MenuItem.query

    if not include_inactive:
        query = query.filter_by(is_active=True)

    if restaurant_id:
        query = query.filter_by(restaurant_id=restaurant_id)

    categories = query.order_by(MenuItem.sort_order).all()
    return jsonify(schema.dump(categories))


# 创建新商品分类
@category_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_category():
    try:
        data = request.validated_data
        # 检查餐厅是否存在
        if not Restaurant.query.get(data.restaurant_id):
            return jsonify({"error": "餐厅不存在"}), ECode.ERROR

        db.session.add(data)
        db.session.commit()
        return jsonify(schema.dump(data)), ECode.SUCC
    except ValidationError as err:
        return jsonify({"errors": err.messages}), ECode.ERROR
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), ECode.INTER


# 获取单个分类详情
@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = MenuItem.query.get_or_404(category_id)
    return jsonify(schema.dump(category))


# 更新商品分类信息"""
@category_bp.route('/<int:category_id>', methods=['PUT'])
@validate_request(schema)
def update_category(category_id):
    category = MenuItem.query.get_or_404(category_id)
    data = request.valiated_data
    for key, value in data.items():
        setattr(category, key, value)
    db.session.commit()
    return jsonify(schema.dump(category)), ECode.SUCC


# 删除商品分类（软删除）
@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = MenuItem.query.get_or_404(category_id)
    try:
        category.is_active = False
        db.session.commit()
        return jsonify({"message": "分类已禁用"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), ECode.INTER


# 获取分类下的所有商品
@category_bp.route('/<int:category_id>/products', methods=['GET'])
def get_category_products(category_id):

    category = MenuItem.query.get_or_404(category_id)
    products = MenuCategory.query.filter_by(category_id=category_id).all()
    return jsonify(OrderSchema.dump(products))
