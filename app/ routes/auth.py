from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed = generate_password_hash(data['password'])
    user = User(username=data['username'], password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify(message="Registered successfully")

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify(token=token)
    return jsonify(message="Invalid credentials"), 401
