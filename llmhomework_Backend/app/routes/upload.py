from flask import Blueprint, request, jsonify, current_app
from app.services.image_processing import preprocess_image
from app.utils.file import save_upload_file
from app.models.record import save_record
from app.config import Config

# 安全导入OCR和AI服务
try:
    from app.services.ocr_engine import smart_extract_questions
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"OCR引擎导入失败: {e}")
    OCR_AVAILABLE = False

try:
    from app.services.grading_new import grade_homework_improved
    GRADING_NEW_AVAILABLE = True
except ImportError as e:
    print(f"新批改引擎导入失败: {e}")
    GRADING_NEW_AVAILABLE = False

try:
    from app.services.grading_qwen import grade_homework_with_ai, get_ai_service_status
    QWEN_AVAILABLE = True
except ImportError as e:
    print(f"Qwen批改引擎导入失败: {e}")
    QWEN_AVAILABLE = False

try:
    from app.services.knowledge_matcher import KnowledgeMatcher
    KNOWLEDGE_MATCHER_AVAILABLE = True
except ImportError as e:
    print(f"知识匹配器导入失败: {e}")
    KNOWLEDGE_MATCHER_AVAILABLE = False
import os
import time
import uuid
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        logger.info("收到上传请求")
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # 获取请求参数
        use_ai = request.form.get('use_ai', 'true').lower() == 'true'
        user_id = request.form.get('user_id', None)
        
        # 生成唯一标识
        task_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        # 保存原图
        save_path = save_upload_file(file, current_app.config['UPLOAD_FOLDER'])
        logger.info(f"图片已保存: {save_path}")
        
        # 图像预处理
        processed_path = preprocess_image(save_path)
        logger.info(f"预处理后图片: {processed_path}")
        
        # 使用OCR识别
        if OCR_AVAILABLE:
            questions = smart_extract_questions(processed_path)
            logger.info(f"识别到 {len(questions)} 道题目")
        else:
            logger.warning("OCR引擎不可用，返回模拟数据")
            questions = [
                {
                    "stem": "示例题目（OCR引擎不可用）",
                    "student_answer": "示例答案",
                    "question_type": "choice"
                }
            ]
        
        # 获取OCR原始文本（用于多模态分析）
        ocr_text = ""
        try:
            with open(processed_path.replace('.jpg', '_ocr.txt'), 'r', encoding='utf-8') as f:
                ocr_text = f.read()
        except:
            ocr_text = " ".join([q.get('stem', '') for q in questions])
        
        # 为每个题目添加唯一标识
        for i, q in enumerate(questions):
            q['question_id'] = f"{task_id}_q_{i}"
            q['timestamp'] = timestamp
        
        # 选择批改方式
        if use_ai and Config.USE_QWEN_GRADING and QWEN_AVAILABLE:
            logger.info("使用 AI 智能批改")
            ai_result = grade_homework_with_ai(questions, ocr_text)
            
            grading_result = ai_result['grading_results']
            knowledge_analysis = ai_result.get('knowledge_analysis', {})
            practice_questions = ai_result.get('practice_questions', [])
            multimodal_analysis = ai_result.get('multimodal_analysis', None)
        elif use_ai and GRADING_NEW_AVAILABLE:
            logger.info("使用改进批改引擎")
            grading_result = grade_homework_improved(questions)
            knowledge_analysis = {}
            practice_questions = []
            multimodal_analysis = None
            
            # 兼容原有格式
            wrong_knowledges = knowledge_analysis.get('wrong_knowledge_points', [])
            
        else:
            logger.info("使用传统批改方式")
            if GRADING_NEW_AVAILABLE:
                grading_result = grade_homework_improved(questions)
            else:
                # 基础批改逻辑
                grading_result = []
                for i, q in enumerate(questions):
                    grading_result.append({
                        'correct': True,  # 默认正确
                        'score': 5,
                        'explanation': '批改引擎不可用，默认正确',
                        'question_id': q.get('question_id', f'q_{i}')
                    })
            
            wrong_knowledges = []  # 暂时为空
            knowledge_analysis = None
            practice_questions = []
            multimodal_analysis = None
        
        # 为批改结果添加题目ID
        for i, result in enumerate(grading_result):
            if i < len(questions):
                result['question_id'] = questions[i]['question_id']
        
        logger.info(f"批改完成，错题知识点: {wrong_knowledges}")
        
        # 计算总结信息
        total_score = sum(r.get('score', 0) for r in grading_result)
        correct_count = sum(1 for r in grading_result if r.get('correct', False))
        accuracy_rate = correct_count / len(grading_result) if grading_result else 0
        
        # 构建符合database_schema.json的记录
        record = {
            'task_id': task_id,
            'timestamp': timestamp,
            'user_id': user_id,
            'questions': questions,
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges,
            'summary': {
                'total_questions': len(questions),
                'correct_count': correct_count,
                'total_score': total_score,
                'accuracy_rate': accuracy_rate
            }
        }
        
        # 如果有AI分析结果，添加到记录中（但只在有实际内容时）
        if use_ai and Config.USE_QWEN_GRADING and (knowledge_analysis or practice_questions or multimodal_analysis):
            ai_data = {}
            if knowledge_analysis:
                ai_data['knowledge_analysis'] = knowledge_analysis
            if practice_questions:
                ai_data['practice_questions'] = practice_questions
            if multimodal_analysis:
                ai_data['multimodal_analysis'] = multimodal_analysis
            
            if ai_data:  # 只有在有数据时才添加
                record['ai_analysis'] = ai_data
        
        save_record(record)
        logger.info("批改记录已保存")
        
        # 构建响应数据
        response_data = {
            'task_id': task_id,
            'timestamp': timestamp,
            'grading_result': grading_result,
            'wrong_knowledges': wrong_knowledges,
            'questions': questions,
            'summary': record['summary'],
            'ai_enabled': use_ai and Config.USE_QWEN_GRADING
        }
        
        # 如果启用了AI功能，添加AI分析结果
        if use_ai and Config.USE_QWEN_GRADING:
            response_data.update({
                'knowledge_analysis': knowledge_analysis,
                'practice_questions': practice_questions,
                'study_suggestions': knowledge_analysis.get('study_recommendations', []) if knowledge_analysis else []
            })
            
            if multimodal_analysis:
                response_data['multimodal_analysis'] = multimodal_analysis
        
        logger.info(f"成功处理上传请求，任务ID: {task_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"处理作业时发生异常: {e}", exc_info=True)
        return jsonify({'error': f'处理作业时发生异常: {str(e)}'}), 500

@upload_bp.route('/ai_status', methods=['GET'])
def get_ai_status():
    """获取AI服务状态"""
    try:
        status = get_ai_service_status()
        return jsonify({
            'status': 'success',
            'ai_service': status
        })
    except Exception as e:
        logger.error(f"获取AI服务状态失败: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@upload_bp.route('/generate_practice', methods=['POST'])
def generate_practice_questions():
    """根据知识点生成练习题"""
    try:
        data = request.get_json()
        knowledge_points = data.get('knowledge_points', [])
        count = data.get('count', 3)
        
        if not knowledge_points:
            return jsonify({'error': '请提供知识点列表'}), 400
        
        # 检查AI服务状态
        status = get_ai_service_status()
        if not status.get('qwen_available', False):
            return jsonify({'error': 'AI服务不可用，无法生成练习题'}), 503
        
        # 导入QwenService来生成练习题
        from app.services.qwen_service import QwenService
        from app.config import Config
        
        qwen_service = QwenService(Config.QWEN_MODEL_NAME)
        practice_questions = qwen_service.generate_practice_questions(knowledge_points, count)
        
        return jsonify({
            'status': 'success',
            'practice_questions': practice_questions,
            'knowledge_points': knowledge_points,
            'generated_count': len(practice_questions)
        })
        
    except Exception as e:
        logger.error(f"生成练习题失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'生成练习题失败: {str(e)}'
        }), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
