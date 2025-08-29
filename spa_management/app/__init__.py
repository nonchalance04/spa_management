import os
from flask import Flask
# from dotenv import load_dotenv
from .extensions import db, socketio
from .routes.customer import customer_bp
from .routes.therapist import therapist_bp
from .routes.cashier import cashier_bp
from .routes.monitor import monitor_bp
from .routes.monitor_snapshot import snapshot_bp
from .routes.auth import auth_bp


def create_app() -> Flask:
    # load_dotenv()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.url_map.strict_slashes = False

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DB", "token_spa")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    async_mode = os.getenv("SOCKETIO_ASYNC_MODE", "threading")
    socketio.init_app(app, async_mode=async_mode, cors_allowed_origins="*")

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(therapist_bp)
    app.register_blueprint(cashier_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(snapshot_bp)
    app.register_blueprint(auth_bp)

    # Import socket.io event handlers
    from . import socketio_events  # noqa: F401

    return app

# Expose socketio for run.py
__all__ = ["create_app", "socketio"]
