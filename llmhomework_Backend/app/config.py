import os
import sys

# 修复Windows编码问题
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # [AI] AI 模型配置 - 直接调用Qwen VL LoRA服务
    # Qwen2.5-VL-32B-Instruct-LoRA-Trained多模态服务 (直接调用)
    QWEN_VL_API_URL = 'http://172.31.179.77:8007'  # LoRA服务器地址
    LLM_PROVIDER = 'qwen_vl_lora_direct'  # 直接调用训练后的LoRA多模态模型
    MULTIMODAL_ENABLED = True  # 启用多模态分析
    USE_QWEN_GRADING = True  # 启用AI批改功能
    
    # 直接调用配置
    USE_DIRECT_LORA_SERVICE = True  # 启用直接调用LoRA服务
    BYPASS_RAG_SERVICE = True  # 绕过RAG中间层
    ENABLE_STRUCTURED_OUTPUT = True  # 启用结构化输出解析
    
    
    # 通用配置
    MAX_TOKENS = 8000  # 优化后的Token数 (Qwen2.5-VL推荐)
    QWEN_MAX_TOKENS = 8000   # 兼容原字段名，优化性能
    TIMEOUT_SECONDS = 300  # 超时时间设置为5分钟（给LoRA模型更多处理时间）
    RETRY_ATTEMPTS = 3  # 重试次数
    
    # 批改配置
    ENABLE_MULTIMODAL = True  # 启用多模态分析
    ENABLE_KNOWLEDGE_ANALYSIS = True  # 启用知识点分析
    ENABLE_PRACTICE_GENERATION = True  # 启用练习题生成
    
    # 数据库配置
    SQLITE_DATABASE_URL = 'sqlite:///database/knowledge_base.db'
    MYSQL_DATABASE_URL = None  # 可选的MySQL数据库URL
    
    # 题库配置
    DEFAULT_QUESTION_BATCH_SIZE = 100  # 默认批处理大小
    MAX_PRACTICE_QUESTIONS = 50  # 最大练习题数量
    DUPLICATE_SIMILARITY_THRESHOLD = 0.8  # 重复检测相似度阈值
    MIN_QUESTION_QUALITY_SCORE = 3.0  # 最低题目质量分数
    
    # OCR配置（Qwen2.5-VL迁移后禁用）
    OCR_FALLBACK_ENABLED = False  # 禁用OCR回退
    OCR_ENABLED = False  # 禁用OCR处理
    USE_OCR_FALLBACK = False  # 禁用OCR备用方案
