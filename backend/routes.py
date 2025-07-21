from flask import Blueprint, request, jsonify, current_app
from .ocr import ocr_image
from .utils import allowed_file, save_upload_file
from transformers.pipelines import pipeline
import os
import logging
from .image_preprocess import preprocess_image

bp = Blueprint('api', __name__)
generator = pipeline('text-generation', model='gpt2')

users = {}
wrong_questions = {}

@bp.route('/upload', methods=['POST'])
def upload():
    try:
        print("收到/upload请求")
        print("request.form:", request.form)
        print("request.files:", request.files)
        file = request.files.get('image')
        username = request.form.get('username', 'test')
        if not file or not file.filename or not allowed_file(file.filename):
            return jsonify({'success': False, 'msg': 'No valid image uploaded'}), 400
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = save_upload_file(file, upload_folder, username)
        print(f"保存图片到: {filepath}")
        # 检查文件是否真的存在
        print("文件是否存在：", os.path.exists(filepath))
        preprocessed_path = filepath.replace('.jpg', '_pre.jpg')
        # 这里调用图片预处理，并传入config参数
        preprocess_image(filepath, preprocessed_path)
        ocr_result = ocr_image(preprocessed_path)
        #os.remove(filepath)
        #os.remove(preprocessed_path)
        # ocr_result 现在是结构化的题目列表
        return jsonify({'success': True, 'questions': ocr_result})
    except Exception as e:
        logging.exception("Upload error")
        return jsonify({'success': False, 'msg': str(e)}), 500

@bp.route('/correct', methods=['POST'])
def correct():
    try:
        data = request.json or {}
        username = data.get('username', 'test')
        user_answers = data.get('answers', [])
        questions = users.get(username, [])
        results, wrongs = [], []
        for i, q in enumerate(questions):
            correct = (user_answers[i].strip() == q['answer'].strip())
            results.append({'question': q['question'], 'your_answer': user_answers[i], 'correct_answer': q['answer'], 'is_right': correct})
            if not correct:
                wrongs.append(q)
        wrong_questions[username] = wrongs
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logging.exception("Correct error")
        return jsonify({'success': False, 'msg': str(e)}), 500

@bp.route('/wrong_questions', methods=['GET'])
def get_wrongs():
    username = request.args.get('username', 'test')
    return jsonify({'success': True, 'wrongs': wrong_questions.get(username, [])})

@bp.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json or {}
        knowledge_point = data.get('knowledge_point', '初中数学分数加减法')
        prompt = f"请为知识点“{knowledge_point}”生成一道初中选择题："
        res = generator(prompt, max_length=50, num_return_sequences=1)
        return jsonify({'success': True, 'question': res[0]['generated_text']})
    except Exception as e:
        logging.exception("Generate error")
        return jsonify({'success': False, 'msg': str(e)}), 500
