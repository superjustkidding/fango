# -*- coding: utf-8 -*-

from flask import Blueprint,jsonify,request
from marshmallow import ValidationError

from app import db
from app.models.restaurants.restaurant import MenuItem, Restaurant
from app.schemas.schemas import MenuItemSchema
from app.utils.validation import validate_request
from extensions.flask_auth import current_user
from lib.ecode import ECode

menu_bp = Blueprint('menus', __name__)
schema = MenuItemSchema()


@menu_bp.route('/',methods=['POST'])
@validate_request(schema)
def create_menus():
    try:
        if current_user._role_name != 'restaurant':
            return jsonify({'error':'You are not allowed to create menus.'}), ECode.FORBID
        data = request.validated_data
        restaurant = Restaurant.query.get(data['restaurant_id'])
        if not restaurant or restaurant.owner_id != current_user.id:
            return jsonify({"error": "无效的餐馆ID或权限不足"}), ECode.FORBID
        menu = MenuItem(**data)
        db.session.add(menu)
        db.session.commit()
        return jsonify(schema.dump(menu)), ECode.SUCC
    except ValidationError as err:
            return jsonify({"error": "数据验证失败", "details": err.messages}), ECode.FORBID
    except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), ECode.INTER


@menu_bp.route('/<int:menu_id>',methods=['GET'])
def get_menu(menu_id):
    menu = MenuItem.query.get_or_404(menu_id)
    return jsonify(schema.dump(menu)), ECode.SUCC


@menu_bp.route('/restaurant/<int:restaurant_id>',methods=['GET'])
def get_restaurant_menu(restaurant_id):
    available_only = request.args.get('available_only', 'false').lower() == 'true'

    query = MenuItem.query.filter_by(restaurant_id=restaurant_id)
    if available_only:
        query = query.filter_by(is_available=True)

    menu = query.order_by(MenuItem.created_at.desc()).all()
    return jsonify(schema.dump(menu))


@menu_bp.route('/<int:menu_id>',methods=['PUT'])
@validate_request(schema)
def update_menu(menu_id):
    menu = MenuItem.query.get_or_404(menu_id)
    if current_user._role_name != 'restaurant':
            return jsonify({"error":"无权修改餐品"}),ECode.FORBID
    data = request.validated_data
    for field in data:
        setattr(menu, field, data[field])
    db.session.commit()
    return jsonify(schema.dump(menu))

@menu_bp.route('/<int:menu_id>',methods=['DELETE'])
def delete_menu(menu_id):
    menu = MenuItem.query.get_or_404(menu_id)
    try:
        if current_user._role_name != 'restaurant' or menu.restaurant.id != current_user.id:
            return jsonify({'error': 'You are not allowed to delete menus.'}), ECode.FORBID
        db.session.delete(menu)
        db.session.commit()
        return jsonify({"success": True}), ECode.SUCC
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), ECode.INTER











