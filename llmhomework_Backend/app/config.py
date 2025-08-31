import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    OCR_LANGUAGES = ['ch_sim', 'en']
    MODEL_PATH = ''  # 可根据需要填写
    SECRET_KEY = 'your_secret_key'
    
    # Llama 模型配置
    LLAMA_MODEL_NAME = 'llama2:13b'
    LLAMA_MODEL_PATH = r'C:\Users\48108\.ollama\models'
    USE_LLAMA_GRADING = True  # 是否使用 Llama 进行智能批改
    LLAMA_MAX_TOKENS = 1000   # Llama 响应的最大 token 数
    
    # 批改配置
    ENABLE_MULTIMODAL = True  # 启用多模态分析
    ENABLE_KNOWLEDGE_ANALYSIS = True  # 启用知识点分析
    ENABLE_PRACTICE_GENERATION = True  # 启用练习题生成