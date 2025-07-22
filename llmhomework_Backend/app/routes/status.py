from flask import Blueprint, jsonify
import importlib

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def status():
    modules = [
        'easyocr', 'pytesseract', 'cv2', 'jieba', 'sklearn', 'transformers', 'torch', 'openai'
    ]
    result = {}
    for m in modules:
        try:
            importlib.import_module(m)
            result[m] = 'ok'
        except Exception as e:
            result[m] = f'error: {e}'
    return jsonify(result) 