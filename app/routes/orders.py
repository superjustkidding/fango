from flask import Blueprint, request, jsonify

from app import db
from app.models import Order
from app.schemas import OrderSchema
from app.utils.validation import validate_request

order_bp = Blueprint('orders', __name__)
schema = OrderSchema()
@order_bp.route('/', methods=['POST'])
@validate_request(schema)
def create_orders():
    data = request.validated_data
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(schema.dump(order)),201

# @order_bp.route('/', methods=['GET'])
# @validate_request(schema)
# def get_orders():
