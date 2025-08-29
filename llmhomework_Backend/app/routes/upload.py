from flask import Blueprint, request, jsonify, current_app
from app.services.image_processing import preprocess_image
from app.services.ocr_engine import smart_extract_questions
# from app.services.text_preprocess import preprocess_ocr_result  # 未使用，已移除
from app.services.grading_new import grade_homework_improved
from app.utils.file import save_upload_file
from app.services.knowledge import summarize_wrong_questions
from app.models.record import save_record
import os
import time
import uuid

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
        
        # 生成唯一标识
        task_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        # 保存原图
        save_path = save_upload_file(file, current_app.config['UPLOAD_FOLDER'])
        print(f"图片已保存: {save_path}", flush=True)
        # 图像预处理
        processed_path = preprocess_image(save_path)
        print(f"预处理后图片: {processed_path}", flush=True)
        
        # 使用OCR识别（移除LLaVA依赖）
        questions = smart_extract_questions(processed_path)
        print(f"结构化题目: {questions}", flush=True)
        
        # 为每个题目添加唯一标识
        for i, q in enumerate(questions):
            q['question_id'] = f"{task_id}_q_{i}"
            q['timestamp'] = timestamp
        
        # 提取题目内容进行批改
        question_texts = [q['stem'] for q in questions]
        grading_result = grade_homework_improved(questions)
        print(f"判题结果: {grading_result}", flush=True)
        
        # 为批改结果添加题目ID
        for i, result in enumerate(grading_result):
            if i < len(questions):
                result['question_id'] = questions[i]['question_id']
        
        wrong_knowledges = summarize_wrong_questions(grading_result)
        print(f"错题知识点: {wrong_knowledges}", flush=True)
        
        record = {
            'task_id': task_id,
            'timestamp': timestamp,
            'questions': questions,
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges
        }
        save_record(record)
        print("批改记录已保存", flush=True)
        
        response_data = {
            'task_id': task_id,
            'timestamp': timestamp,
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges,
            'questions': questions
        }
        print(f"返回给前端的数据: {response_data}", flush=True)
        return jsonify(response_data)
    except Exception as e:
        print(f"处理作业时发生异常: {e}", flush=True)
        return jsonify({'error': f'处理作业时发生异常: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
