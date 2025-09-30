from flask import Flask
from flask_cors import CORS
from .config import Config
import logging
import os

# 延迟导入路由，避免在导入时触发服务初始化

# 腾讯云OCR测试
def test_tencent_ocr_connection():
    """测试腾讯云OCR连接状态"""
    try:
        from .services.tencent_ocr_service import TencentOCRService
        
        # 创建OCR服务实例
        ocr_service = TencentOCRService()
        
        # 简单测试：获取客户端实例
        client = ocr_service._get_client()
        if client:
            # 简化输出，减少噪音
            logging.info("腾讯云OCR服务初始化成功 (备用)")
            return True
        else:
            logging.warning("腾讯云OCR客户端创建失败")
            return False
            
    except ImportError:
        logging.warning("腾讯云OCR SDK未安装")
        return False
    except Exception as e:
        logging.warning(f"腾讯云OCR连接测试失败: {str(e)}")
        return False

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
    
    # 延迟导入并注册蓝图（避免导入时的服务初始化）
    from .routes.upload import upload_bp
    from .routes.result import result_bp
    from .routes.status import status_bp
    from .routes.classify import classify_bp
    from .api.knowledge_endpoints import knowledge_api
    from .api.question_bank_endpoints import question_bank_bp
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(classify_bp)
    app.register_blueprint(knowledge_api)
    app.register_blueprint(question_bank_bp)
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 测试腾讯云OCR连接（备用服务）
    test_tencent_ocr_connection()
    
    return app
