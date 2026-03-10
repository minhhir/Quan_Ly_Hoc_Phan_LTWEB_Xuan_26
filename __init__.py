from flask import Flask
from database import init_auth_tables


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hihi'
    init_auth_tables()

    from admin.routes import admin_bp
    from auth.routes import auth_bp
    from client.routes import client_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)

    return app