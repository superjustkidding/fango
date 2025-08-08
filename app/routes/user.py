from flask import Blueprint, jsonify, request

from app import db
from app.models import User
from app.schemas import UserSchema, InternalUserSchema, ExternalUserSchema
from app.utils.validation import validate_request

user_bp = Blueprint('user', __name__)
schema = UserSchema()

# 获取所有用户
@user_bp.route("/",methods=["GET"])
def get_users():
    user = User.query.all()
    return jsonify(schema.dump(user))


# 创建用户
@user_bp.route("/",methods=["POST"])
@validate_request(schema)
def create_user():
    data = request.validated_data
    user_type = data.pop('type')
    if user_type == 'internal':
        internal_data = InternalUserSchema().load(data)
        user = User(**internal_data)
        schema = InternalUserSchema()

    else:
        external_data = ExternalUserSchema().load(data)
        user = User(**external_data)
        schema = ExternalUserSchema()
    db.session.add(user)
    db.session.commit()
    return jsonify(schema.dump(user)),201


# 获取单个用户详情
@user_bp.route("/<int:user_id>",methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.type == 'internal':
        schema = InternalUserSchema()
    else:
        schema = ExternalUserSchema()
    return jsonify(schema.dump(user))


# 更新用户信息
@user_bp.route("/<int:user_id>",methods=["PUT"])
@validate_request(schema)
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.type == 'internal':
        schema = InternalUserSchema()
    else:
        schema = ExternalUserSchema()
    data  =  request.validated_data
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify(schema.dump(user))


# 删除用户信息
@user_bp.route('/<int:user_id>',methods=["DELETE"])
@validate_request(schema)
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


