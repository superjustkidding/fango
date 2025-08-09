# from flask import Blueprint, jsonify, request
# from marshmallow import ValidationError
# from app import db
# from app.models import User
# from app.schemas import UserSchema
# from app.utils.validation import validate_request
# from extensions.flask_auth import current_user
# from lib.ecode import ECode
#
# user_bp = Blueprint('user', __name__)
# schema = UserSchema()
#
#
#
#
#
# @user_bp.route('/me', methods=['GET'])
# def get_current_user():
#     """获取当前用户信息"""
#     if current_user.role == 'customer':
#         return jsonify(CustomerSchema.dump(current_user))
#     elif current_user.role == 'merchant':
#         return jsonify(MerchantSchema.dump(current_user))
#     elif current_user.role == 'courier':
#         return jsonify(CourierSchema.dump(current_user))
#     else:
#         return jsonify(Admin.dump(current_user))
#
#
# # 顾客注册
# @user_bp.route('/customers/register', methods=['POST'])
# @validate_request(schema)
# def register_customer():
#     try:
#         data = request.validated_data
#         if User.query.filter_by(username=data['username']).first():
#             return jsonify({"error": "用户名已存在"}), ECode.ERROR
#
#         customer = Customer(**data)
#         customer.password = data['password']
#
#         db.session.add(customer)
#         db.session.commit()
#         return jsonify(CustomerSchema.dump(customer)), ECode.SUCC
#     except ValidationError as err:
#         return jsonify({"error": err.messages}), ECode.ERROR
#
#
# # 商家注册
# @user_bp.route('/merchants/register', methods=['POST'])
# def register_merchant():
#     try:
#         data = request.validated_data
#         if User.query.filter_by(username=data['username']).first():
#             return jsonify({"error": "用户名已存在"}), ECode.ERROR
#
#         merchant = Merchant(**data)
#         merchant.password = data['password']
#
#         db.session.add(merchant)
#         db.session.commit()
#         return jsonify(MerchantSchema.dump(merchant)), ECode.SUCC
#     except ValidationError as err:
#         return jsonify({"error": err.messages}), ECode.ERROR
#
#
# # 骑手注册（通常由管理员添加）
# @user_bp.route('/couriers', methods=['POST'])
#
# def create_courier():
#     if current_user.role != 'admin':
#         return jsonify({"error": "无权操作"}), ECode.FORBID
#
#     try:
#         data = request.validated_data
#         if User.query.filter_by(username=data['username']).first():
#             return jsonify({"error": "用户名已存在"}), ECode.ERROR
#
#         courier = Courier(**data)
#         courier.password = data['password']
#
#         db.session.add(courier)
#         db.session.commit()
#         return jsonify(CourierSchema.dump(courier)), ECode.SUCC
#     except ValidationError as err:
#         return jsonify({"error": err.messages}), ECode.ERROR
#
#
# # 管理员获取用户列表
# @user_bp.route('/', methods=['GET'])
#
# def get_users():
#     if current_user.role != 'admin':
#         return jsonify({"error": "无权操作"}), ECode.FORBID
#
#     role = request.args.get('role')
#     query = User.query
#
#     if role in ['customer', 'merchant', 'courier', 'admin']:
#         query = query.filter_by(role=role)
#
#     users = query.all()
#
#     result = []
#     for user in users:
#         if user.role == 'customer':
#             result.append(CustomerSchema.dump(user))
#         elif user.role == 'merchant':
#             result.append(MerchantSchema.dump(user))
#         elif user.role == 'courier':
#             result.append(CourierSchema.dump(user))
#         else:
#             result.append(Admin.dump(user))
#
#     return jsonify(result)
#
#
# # 更新当前用户信息
# @user_bp.route('/update_information', methods=['PUT'])
# def update_profile():
#     try:
#         # 根据用户角色选择对应的Schema
#         if current_user.role == 'merchant':
#             schema = MerchantSchema
#             model = Merchant
#         elif current_user.role == 'courier':
#             schema = CourierSchema
#             model = Courier
#         elif current_user.role == 'admin':
#             schema = Admin
#             model = Admin
#         else:
#             return jsonify({"error": "未知用户角色"}), ECode.ERROR
#
#         # 部分更新（partial=True允许只传部分字段）
#         data = schema.load(request.json, partial=True)
#
#         # 获取当前用户的具体实例（Merchant/Courier/Admin）
#         user = model.query.get(current_user.id)
#
#         # 更新字段（排除密码字段单独处理）
#         for field, value in data.items():
#             if field != 'password':
#                 setattr(user, field, value)
#
#         # 特殊处理密码修改
#         if 'password' in data:
#             user.password = data['password']
#
#         db.session.commit()
#
#         return jsonify(schema.dump(user))
#
#     except ValidationError as err:
#         return jsonify({"error": "数据验证失败", "details": err.messages}), ECode.ERROR
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), ECode.INTER
#
#
# @user_bp.route('/delete_account', methods=['DELETE'])
# def admin_delete():
#     try:
#         # 获取用户具体实例
#         if current_user.role == 'merchant':
#             user = Merchant.query.get(current_user.id)
#         elif current_user.role == 'courier':
#             user = Courier.query.get(current_user.id)
#         elif current_user.role == 'admin':
#             user = Admin.query.get(current_user.id)
#         else:
#             return jsonify({"error": "未知用户类型"}), ECode.FORBID
#
#         # 执行软删除（推荐）
#         user.is_active = False
#
#         # 或者执行硬删除（谨慎使用）
#         # db.session.delete(user)
#
#         db.session.commit()
#         # logout_user()  # 登出当前会话
#
#         return jsonify({"message": "账户已成功注销"})
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500
#
