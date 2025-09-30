from flask import Blueprint, request, jsonify, current_app
import os
import logging
import uuid
from datetime import datetime
import json
from typing import Dict, Any, List, Optional

from app.config import Config
from app.services.multimodal_client import analyze_homework_with_direct_service
from app.services.image_processing import preprocess_image

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

def _ensure_list(value):
    """确保值是列表格式"""
    if value is None:
        return []
    if isinstance(value, str):
        # 处理用分隔符分割的字符串
        if ',' in value:
            return [item.strip() for item in value.split(',') if item.strip()]
        elif '、' in value:
            return [item.strip() for item in value.split('、') if item.strip()]
        else:
            return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return value
    return [str(value)]

def _enhance_grading_payload(grading_payload: Dict[str, Any]) -> Dict[str, Any]:
    """增强批改结果的数据结构"""
    results = grading_payload.get("grading_result") or []
    questions = grading_payload.get("questions") or []
    
    # 确保results是列表
    if not isinstance(results, list):
        results = [results] if results else []
    
    # 为每个结果添加默认值和增强字段
    correct_count = 0
    aggregated_knowledge_points = set()
    main_issues = []
    
    for i, result in enumerate(results):
        if not isinstance(result, dict):
            continue
            
        # 基础字段处理
        result.setdefault("correct", False)
        result.setdefault("score", 0)
        result.setdefault("explanation", "")
        result.setdefault("knowledge_points", [])
        result.setdefault("type", "未知题型")
        
        # 确保知识点是列表
        result["knowledge_points"] = _ensure_list(result["knowledge_points"])
        
        # 保留新字段（learning_suggestions, similar_question）
        if "learning_suggestions" in result:
            result["learning_suggestions"] = _ensure_list(result["learning_suggestions"])
        if "similar_question" in result:
            # similar_question 保持原样
            pass
        
        # 统计数据
        if result["correct"]:
            correct_count += 1
        aggregated_knowledge_points.update(result.get("knowledge_points") or [])
        if not result["correct"]:
            question_text = result.get("question", "")
            if question_text:
                main_issues.append(f"题目: {question_text[:40]}...")

    # 处理questions数组
    for question in questions:
        if isinstance(question, dict):
            # 保留 questions 中的新字段
            if "similar_question" in question:
                # similar_question 保持原样
                pass

    # 处理summary
    summary = grading_payload.get("summary") or {}
    summary.setdefault("total_questions", len(results) or len(questions))
    summary["correct_count"] = correct_count
    total_questions = summary.get("total_questions") or len(results) or 1
    summary["accuracy_rate"] = correct_count / total_questions if total_questions else 0
    summary["main_issues"] = _ensure_list(summary.get("main_issues")) or main_issues
    summary["knowledge_points"] = _ensure_list(summary.get("knowledge_points")) or list(aggregated_knowledge_points)
    
    # 保留 summary 中的新字段
    if "learning_suggestions" in summary:
        summary["learning_suggestions"] = _ensure_list(summary["learning_suggestions"])
    if "similar_question" in summary:
        # similar_question 保持原样
        pass

    grading_payload["grading_result"] = results
    grading_payload["summary"] = summary

    # 知识点分析兜底
    knowledge_analysis = grading_payload.get("knowledge_analysis") or {}
    wrong_points = _ensure_list(knowledge_analysis.get("wrong_knowledge_points"))
    study_recommendations = _ensure_list(knowledge_analysis.get("study_recommendations"))

    if not wrong_points:
        wrong_points = [kp for kp in aggregated_knowledge_points if kp]
    if not study_recommendations and wrong_points:
        study_recommendations = [f"复习相关知识点：{kp}" for kp in wrong_points]

    knowledge_analysis["wrong_knowledge_points"] = wrong_points
    knowledge_analysis["study_recommendations"] = study_recommendations
    grading_payload["knowledge_analysis"] = knowledge_analysis

    return grading_payload

@upload_bp.route('/upload_image', methods=['POST'])
def upload_image():
    """
    图片上传和AI批改端点 - 简化版（仅使用直接LoRA调用）
    """
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
        
        # 生成任务ID和时间戳
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        cache_bust_id = str(uuid.uuid4())
        
        logger.info(f"🆔 任务ID: {task_id}")
        logger.info(f"🔄 缓存破坏ID: {cache_bust_id}")

        # 保存文件
        filename = f"{task_id}_{file.filename}"
        save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file.save(save_path)
        
        logger.info(f"📁 文件保存到: {save_path}")

        # 🎯 使用Qwen VL LoRA直接调用服务进行分析
        logger.info("🎯 开始使用Qwen VL LoRA直接调用服务...")
        
        # 为多模态AI处理图片（保留彩色）
        multimodal_processed_path = preprocess_image(save_path, for_multimodal=True)
        logger.info(f"📁 多模态预处理后图片: {multimodal_processed_path}")
        
        # 验证文件路径和大小
        if not os.path.exists(multimodal_processed_path):
            raise Exception(f"预处理后的图片文件不存在: {multimodal_processed_path}")
        
        file_size = os.path.getsize(multimodal_processed_path)
        logger.info(f"📊 图片文件大小: {file_size} 字节")
        
        if file_size == 0:
            raise Exception("图片文件为空")
                
        # 🚀 调用Qwen VL LoRA直接服务进行分析
        logger.info(f"🚀 开始调用Qwen VL LoRA直接服务，文件路径: {multimodal_processed_path}")
        ai_result = analyze_homework_with_direct_service(multimodal_processed_path)
        
        if not ai_result.get("success"):
            # 检查是否是无内容识别的情况
            if ai_result.get("error_type") == "no_content":
                logger.warning("⚠️ 图片内容无法识别")
                return jsonify({
                    'error': ai_result.get("error", "图片中无法识别到有效的题目内容"),
                    'error_type': 'no_content',
                    'processing_method': 'qwen_vl_lora_no_content',
                    'questions': [],
                    'grading_result': [],
                    'summary': ai_result.get("summary", {}),
                    'task_id': task_id,
                    'timestamp': timestamp
                }), 400
            else:
                raise Exception(f"Qwen VL LoRA分析失败: {ai_result.get('error', '未知错误')}")
        
        logger.info(f"✅ Qwen VL LoRA直接调用成功，用时: {ai_result.get('processing_time', 0):.2f}秒")
        
        # 🎯 处理成功的结果
        questions = ai_result.get("questions", [])
        grading_result_data = ai_result.get("grading_result", [])
        summary_data = ai_result.get("summary", {})
        knowledge_analysis_data = ai_result.get("knowledge_analysis", {})
        
        # 构建完整的批改结果
        grading_result = _enhance_grading_payload({
            "grading_result": grading_result_data,
            "questions": questions,
            "summary": summary_data,
            "knowledge_analysis": knowledge_analysis_data,
            "method": "qwen_vl_lora_direct"
        })
        
        # 为每个题目添加唯一标识
        for i, q in enumerate(questions):
            if not q.get('question_id'):
                q['question_id'] = f"{task_id}_q_{i}"
                q['timestamp'] = timestamp
        
        # 🎯 设置多模态分析信息
        multimodal_analysis = {
            "method": "qwen_vl_lora_direct",
            "analysis": "使用Qwen2.5-VL-32B-Instruct-LoRA-Trained直接分析图片完成识别和批改",
            "accuracy": "高精度多模态图片理解",
            "model": "Qwen2.5-VL-32B-Instruct-LoRA-Trained",
            "analysis_type": "lora_multimodal"
        }
        
        # 获取最终结果
        final_grading_result = grading_result["grading_result"]
        knowledge_analysis = grading_result["knowledge_analysis"]
        practice_questions = []  # 多模态AI暂不生成练习题
        
        # 从多个来源获取错题知识点
        wrong_knowledges = knowledge_analysis.get('wrong_knowledge_points', [])
        
        # 🚀 构建最终响应数据
        response_data = {
            'task_id': task_id,
            'timestamp': timestamp,
            'cache_bust_id': cache_bust_id,
            'questions': questions,
            'grading_result': final_grading_result,
            'summary': grading_result.get("summary", {}),
            'wrong_knowledges': wrong_knowledges,
            'processing_method': 'qwen_vl_lora_direct',
            'ai_enabled': True,
            'knowledge_analysis': knowledge_analysis,
            'practice_questions': practice_questions,
            'study_suggestions': knowledge_analysis.get('study_recommendations', [])
        }
        
        # 🚀 添加直接调用服务的新字段
        response_data.update({
            'learning_suggestions': ai_result.get('learning_suggestions', []),
            'similar_questions': ai_result.get('similar_questions', [])
        })
            
        logger.info(f"✅ 添加新字段 - learning_suggestions: {len(ai_result.get('learning_suggestions', []))}条")
        logger.info(f"✅ 添加新字段 - similar_questions: {len(ai_result.get('similar_questions', []))}道")
        
        # 添加多模态分析信息
        response_data['multimodal_analysis'] = multimodal_analysis
        
        logger.info(f"✅ 作业批改完成！题目数量: {len(questions)}, 处理方法: qwen_vl_lora_direct")
        
        # 设置响应头防止缓存
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Request-ID'] = cache_bust_id
        
        return response
        
    except Exception as e:
        logger.error(f"处理作业时发生异常: {e}", exc_info=True)
        return jsonify({'error': f'处理作业时发生异常: {str(e)}'}), 500

@upload_bp.route('/ai_status', methods=['GET'])
def get_ai_status():
    """获取AI服务状态"""
    try:
        # 延迟导入避免启动时的日志噪音
        try:
            from app.services.grading_qwen import get_ai_service_status
            status = get_ai_service_status()
        except ImportError:
            # 如果导入失败，返回基本状态
            status = {
                "qwen_service": "available",
                "multimodal_service": "available", 
                "processing_method": "qwen_vl_lora_direct"
            }
        
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

@upload_bp.route('/health/multimodal', methods=['GET'])
def check_multimodal_health():
    """检查Qwen2.5-VL多模态服务健康状态"""
    try:
        from app.services.multimodal_client import get_qwen_vl_client
        
        qwen_vl_client = get_qwen_vl_client()
        health_result = qwen_vl_client.health_check()
        
        return jsonify({
            "local_status": "healthy" if health_result.get("status") == "healthy" else "unhealthy",
            "remote_service": health_result,
            "model_type": "Qwen2.5-VL-32B-Instruct-LoRA-Trained",
            "connection": "connected" if health_result.get("status") == "healthy" else "disconnected",
            "api_url": Config.QWEN_VL_API_URL,
            "config": {
                "llm_provider": Config.LLM_PROVIDER,
                "multimodal_enabled": Config.MULTIMODAL_ENABLED,
                "use_qwen_grading": Config.USE_QWEN_GRADING,
                "ocr_fallback_enabled": getattr(Config, 'OCR_FALLBACK_ENABLED', False),
                "max_tokens": Config.MAX_TOKENS,
                "timeout_seconds": Config.TIMEOUT_SECONDS
            }
        })
    except Exception as e:
        logger.error(f"多模态健康检查失败: {e}")
        return jsonify({
            "local_status": "error",
            "error": str(e),
            "model_type": "Qwen2.5-VL-32B-Instruct-LoRA-Trained",
            "connection": "failed"
        }), 500

@upload_bp.route('/generate_practice', methods=['POST'])
def generate_practice_questions():
    """生成练习题"""
    try:
        data = request.get_json()
        knowledge_points = data.get('knowledge_points', [])
        count = data.get('count', 3)
        
        logger.info(f"生成练习题请求: 知识点={knowledge_points}, 数量={count}")
        
        # 延迟导入避免循环依赖
        try:
            from app.services.grading_qwen import get_ai_service_status
            get_ai_service_status()
        except ImportError as e:
            logger.warning(f"无法导入AI服务状态检查: {e}")
        
        # 简单的练习题生成逻辑
        practice_questions = []
        for i, kp in enumerate(knowledge_points[:count]):
            practice_questions.append({
                'id': f'practice_{i+1}',
                'question': f'关于"{kp}"的练习题 {i+1}',
                'knowledge_point': kp,
                'difficulty': 'medium',
                'type': '计算题'
            })
        
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
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']