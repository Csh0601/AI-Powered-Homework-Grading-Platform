from flask import Blueprint, request, jsonify, current_app
from app.services.image_processing import preprocess_image
from app.services.ocr_engine import ocr_image
from app.services.text_preprocess import preprocess_ocr_result
from app.services.grading import grade_homework
from app.utils.file import save_upload_file
from app.services.knowledge import summarize_wrong_questions
from app.models.record import save_record
import os

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        print("收到上传请求", flush=True)
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        # 保存原图
        save_path = save_upload_file(file, current_app.config['UPLOAD_FOLDER'])
        print(f"图片已保存: {save_path}", flush=True)
        # 图像预处理
        processed_path = preprocess_image(save_path)
        print(f"预处理后图片: {processed_path}", flush=True)
        # OCR识别（可切换mode）
        ocr_lines = ocr_image(processed_path, mode='easyocr')
        print(f"OCR结果: {ocr_lines}", flush=True)
        # 文本预处理
        preprocessed = preprocess_ocr_result(ocr_lines)
        print(f"文本预处理: {preprocessed}", flush=True)
        # 判题
        grading_result = grade_homework([item['raw'] for item in preprocessed])
        print(f"判题结果: {grading_result}", flush=True)
        # 错题分析
        wrong_knowledges = summarize_wrong_questions(grading_result)
        print(f"错题知识点: {wrong_knowledges}", flush=True)
        # 保存批改记录
        record = {
            'ocr_result': ocr_lines,
            'preprocessed': preprocessed,
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges
        }
        save_record(record)
        print("批改记录已保存", flush=True)
        return jsonify({
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges
        })
    except Exception as e:
        print(f"处理作业时发生异常: {e}", flush=True)
        return jsonify({'error': f'处理作业时发生异常: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
