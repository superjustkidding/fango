from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)

    from .routes import auth, orders
    app.register_blueprint(auth.bp)
    #app.register_blueprint(meals.bp)
    app.register_blueprint(orders.bp)

    return app
