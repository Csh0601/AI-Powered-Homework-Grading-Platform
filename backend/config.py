import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB










