from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Order, OrderItem
from app.schemas import OrderSchema, OrderItemSchema
from app.utils.validation import validate_request

order_bp = Blueprint('orders', __name__)
schema = OrderSchema()

# 获取订单详情（带关联项）
@order_bp.route('/<int:order_id>',methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    order_data = OrderSchema().dump(order)
    order_data['items'] = OrderItemSchema.dump(order.items)
    return jsonify(order_data)

# 获取用户订单列表（分页+状态过滤）
@order_bp.route('/user/<int:user_id>', methods=['GET'])
@validate_request(schema)
def get_user_orders(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        query = Order.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'items': schema.dump(orders.items),
            'total': orders.total,
            'pages': orders.pages,
            'current_page': orders.page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@order_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_orders():
    try:

        data = request.validated_data
        total = sum(item['price'] * item['quantity'] for item in data['items'])
        order = Order(
            user_id=data['user_id'],
            restaurant_id=data['restaurant_id'],
            total=total,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # 获取order.id
        for item_data in data['items']:
            item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(item)
        db.session.commit()
        return jsonify(schema.dump(order)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# @order_bp.route('/<int:order_id>/status', methods=['PATCH'])
# def update_order_status(order_id):
#     try:
#         order = Order.query.get_or_404(order_id)
#         new_status = request.json.get('status')
#
#         # 状态转换规则
#         valid_transitions = {
#             'pending': ['preparing', 'cancelled'],
#             'preparing': ['delivering', 'cancelled'],
#             'delivering': ['complete'],
#             'complete': [],
#             'cancelled': []
#         }
#
#         # 验证状态转换是否合法
#         if new_status not in valid_transitions.get(order.status, []):
#             return jsonify({
#                 'error': 'Invalid status transition',
#                 'current': order.status,
#                 'allowed': valid_transitions[order.status]
#             }), 400
#
#         order.status = new_status
#         db.session.commit()
#
#         return jsonify(OrderSchema().dump(order))
#
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)

    # 先删除关联的订单项
    OrderItem.query.filter_by(order_id=order_id).delete()

    # 再删除订单
    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Order deleted successfully'}), 200

