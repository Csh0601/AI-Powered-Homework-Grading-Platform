import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    OCR_LANGUAGES = ['ch_sim', 'en']
    MODEL_PATH = ''  # 可根据需要填写
    SECRET_KEY = 'your_secret_key'
