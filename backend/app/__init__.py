import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(
        os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24 * 60 * 60)
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(app.instance_path, 'warehouse.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    origins = [i.strip() for i in cors_origins.split(',') if i.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.items import items_bp
    from app.routes.inbound import inbound_bp
    from app.routes.outbound import outbound_bp
    from app.routes.inventory import inventory_bp
    from app.routes.statistics import statistics_bp
    from app.routes.users import users_bp
    from app.routes.backup import backup_bp
    from app.routes.receiver import receiver_bp
    from app.routes.public import public_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(items_bp, url_prefix='/api/items')
    app.register_blueprint(inbound_bp, url_prefix='/api/inbound')
    app.register_blueprint(outbound_bp, url_prefix='/api/outbound')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')
    app.register_blueprint(receiver_bp, url_prefix='/api/receiver')
    app.register_blueprint(public_bp, url_prefix='/api/public')

    with app.app_context():
        db.create_all()
        from app.utils.init_data import init_database
        init_database()

    return app