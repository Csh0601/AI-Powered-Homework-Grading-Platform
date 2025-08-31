from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes.upload import upload_bp
from .routes.result import result_bp
# from .routes.generate import generate_bp  # 暂时禁用题目生成功能
from .routes.status import status_bp
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app)
    
    # 配置日志
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    
    # 注册蓝图
    app.register_blueprint(upload_bp)
    app.register_blueprint(result_bp)
    # app.register_blueprint(generate_bp)  # 暂时禁用题目生成功能
    app.register_blueprint(status_bp)
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
