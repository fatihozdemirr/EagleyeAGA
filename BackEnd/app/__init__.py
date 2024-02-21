from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from .config import Config
# from app.utils.utils import get_logged_in_user

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

from .main import main_bp 

# @main_bp.context_processor
# def inject_user():
#     return dict(get_logged_in_user=get_logged_in_user)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app)
    db.init_app(app)
    
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

app= create_app()