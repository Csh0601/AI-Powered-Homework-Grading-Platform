import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    OCR_LANGUAGES = ['ch_sim', 'en']
    MODEL_PATH = ''  # 可根据需要填写
    SECRET_KEY = 'your_secret_key'
    
    # Qwen 模型配置
    QWEN_MODEL_NAME = 'qwen3:30B'  # Qwen 模型名称
    OLLAMA_BASE_URL = 'http://172.28.138.140:11434'  # 远程Ollama服务器地址
    SERVER_HOST = '172.28.138.140'  # 服务器主机地址
    OLLAMA_PORT = 11434  # Ollama 服务端口
    USE_QWEN_GRADING = True  # 是否使用 Qwen 进行智能批改
    QWEN_MAX_TOKENS = 2000   # Qwen 响应的最大 token 数
    
    # 批改配置
    ENABLE_MULTIMODAL = True  # 启用多模态分析
    ENABLE_KNOWLEDGE_ANALYSIS = True  # 启用知识点分析
    ENABLE_PRACTICE_GENERATION = True  # 启用练习题生成