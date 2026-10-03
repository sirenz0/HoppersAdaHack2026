from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.donations import donations_bp
    from app.routes.volunteers import volunteers_bp
    from app.routes.recipients import recipients_bp
    from app.routes.map import map_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(donations_bp)
    app.register_blueprint(volunteers_bp)
    app.register_blueprint(recipients_bp)
    app.register_blueprint(map_bp)

    return app
