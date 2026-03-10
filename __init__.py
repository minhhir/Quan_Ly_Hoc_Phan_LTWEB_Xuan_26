from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hihi'

    from .admin.routes import admin_bp
    from .client.routes import client_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)

    return app