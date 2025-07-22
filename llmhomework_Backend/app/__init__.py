from flask import Flask
from .config import Config
from .routes.upload import upload_bp
from .routes.result import result_bp
from .routes.generate import generate_bp
from .routes.status import status_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(upload_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(status_bp)
    return app
