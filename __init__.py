from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Import models
        from app import models

        # Create tables
        db.create_all()

        # Import and register blueprints
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app
