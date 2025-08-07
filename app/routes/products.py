from flask import Blueprint,jsonify,request

from app import db
from app.models import Product, P_Category
from app.schemas import ProductSchema
from app.utils.validation import validate_request

products_bp = Blueprint('products', __name__)
schema = ProductSchema()

@products_bp.route('/<int:id>', methods=['GET'])
def get_products(id):
    products = Product.query.get_or_404(id)
    return jsonify(schema.dump(products)),200


@products_bp.route('/', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    products = Product.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'items': schema.dump(products.items, many=True),
        'total': products.total,
        'pages': products.pages
    })


@products_bp.route('/',methods=['POST'])
@validate_request(schema)
def create_products():
    try:
        data = request.validated_data
        # 验证数据
        errors = schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return schema.jsonify(schema.dump(product)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route('/<int:id>',methods=['PUT'])
@validate_request(schema)
def update_products(id):
    product = Product.query.get_or_404(id)
    data = request.validated_data
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(schema.dump(product)), 200


@products_bp.route('/<int:id>',methods=['DELETE'])
@validate_request(schema)
def delete_products(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify(schema.dump(product)), 200


