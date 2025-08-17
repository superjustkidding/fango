# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.orders.order import Order, OrderItem
from app.models.restaurants.restaurant import Restaurant
from app.schemas.schemas import OrderSchema, OrderItemSchema
from app.utils.validation import validate_request
from extensions.flask_auth import current_user
from lib.ecode import ECode

order_bp = Blueprint('orders', __name__)
schema = OrderSchema()


#
@order_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_orders():
    try:
        data = request.validated_data
        restaurant = Restaurant.query.filter_by(
            id=data['restaurant_id'],
            is_active=True,
            deleted=False
        ).first_or_404()
        order = Order(**data)
        # 处理订单项
        total_amount = 0
        for item_data in data['items']:
            menu_item = OrderItem.query.filter_by(
                id=item_data['menu_item_id'],
                is_available=True,
                restaurant_id=restaurant.id
            ).first_or_404()
        # 创建订单项
        order_item = OrderItem(
            menu_item_id=menu_item.id,
            quantity=item_data['quantity'],
            price_at_order=menu_item.price  # 记录下单时的价格
        )
        order.items.append(order_item)
        total_amount += menu_item.price * item_data['quantity']

        # 更新订单总金额
        order.total_amount = total_amount

        db.session.add(order)
        db.session.commit()
        return jsonify(schema.dump(order)), ECode.SUCC
    except ValidationError as err:
        return jsonify({"error": "数据验证失败"}), ECode.ERROR


@order_bp.route('/<string:order_uuid>', methods=['GET'])
def get_orders(order_uuid):
    order = Order.query.filter_by(uuid=order_uuid).first_or_404()
    if (current_user._role_name != 'users' and order.user_id != current_user.id) or \
        (current_user._role_name != 'restaurant' and order.restaurant_id != current_user.id):
        return  jsonify({'error':'无权查看订单'}), ECode.FORBID
    return jsonify(schema.dump(order)), ECode.SUCC


@order_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):

    # 权限验证
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({"error": "无权查看他人订单"}), ECode.FORBID

    status = request.args.get('status')
    query = Order.query.filter_by(user_id=user_id, deleted=False)

    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify(schema.dump(orders))




