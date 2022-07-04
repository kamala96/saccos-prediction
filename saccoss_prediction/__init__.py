import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
UPLOAD_FOLDER = 'datasets'
MODELS_FOLDER = 'prediction-models'
MODELS_PICS_FOLDER = os.path.join('saccoss_prediction/static', 'model-pics')

# This is the first file that get called when a project is runned
# Very useful when you want to set-up features only once


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MODELS_FOLDER'] = MODELS_FOLDER
    app.config['MODELS_PICS_FOLDER'] = MODELS_PICS_FOLDER

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Communicate with other files. This is all about to register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .generate_model import generate_model as generate_model_blueprint
    app.register_blueprint(generate_model_blueprint)

    from .reporting import reporting as reporting_blueprint
    app.register_blueprint(reporting_blueprint)

    return app
