"""
试卷生成API端点
提供试卷生成和下载的REST API接口
"""

from flask import Blueprint, request, jsonify, send_file
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any

from app.services.paper_generator import generate_paper_from_history, get_paper_generator
from app.models.record import get_records

logger = logging.getLogger(__name__)

# 创建蓝图
paper_bp = Blueprint('paper', __name__, url_prefix='/api/paper')


@paper_bp.route('/generate', methods=['POST'])
def generate_paper():
    """
    生成试卷PDF
    
    请求体：
    {
        "user_id": "用户ID（可选）",
        "max_questions": 10,  # 可选，默认10
        "title": "练习试卷"  # 可选，默认"练习试卷"
    }
    
    返回：
    PDF文件流，可直接下载
    """
    try:
        logger.info("📨 收到生成试卷请求")
        
        # 获取请求参数
        data = request.json if request.json else {}
        user_id = data.get('user_id')
        max_questions = data.get('max_questions', 10)
        title = data.get('title', '练习试卷')
        
        # 验证参数
        if not isinstance(max_questions, int) or max_questions < 1 or max_questions > 50:
            return jsonify({
                'success': False,
                'error': '题目数量必须在1-50之间'
            }), 400
            
        logger.info(f"📋 参数: user_id={user_id}, max_questions={max_questions}, title={title}")
        
        # 1. 获取历史记录
        try:
            records = get_records(user_id=user_id)
            logger.info(f"📚 获取到 {len(records)} 条历史记录")
        except Exception as e:
            logger.error(f"❌ 获取历史记录失败: {e}")
            return jsonify({
                'success': False,
                'error': f'获取历史记录失败: {str(e)}'
            }), 500
            
        if not records:
            return jsonify({
                'success': False,
                'error': '没有找到历史记录，请先完成作业批改'
            }), 404
            
        # 2. 生成试卷PDF
        try:
            pdf_buffer = generate_paper_from_history(
                history_records=records,
                max_questions=max_questions,
                title=title
            )
            
            logger.info(f"✅ 试卷PDF生成成功")
            
            # 3. 返回PDF文件
            filename = f"exam_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
            
        except ValueError as e:
            # 题目不足等业务错误
            logger.warning(f"⚠️ 生成试卷失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
            
        except Exception as e:
            # 其他错误
            logger.error(f"❌ 生成PDF失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'生成试卷失败: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ 处理生成试卷请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@paper_bp.route('/preview', methods=['POST'])
def preview_paper():
    """
    预览试卷信息（不生成PDF，只返回题目列表）
    
    请求体：
    {
        "user_id": "用户ID（可选）",
        "max_questions": 10
    }
    
    返回：
    {
        "success": true,
        "questions": [...],
        "total_found": 15,
        "will_use": 10,
        "message": "找到15道题目，将使用其中10道"
    }
    """
    try:
        logger.info("📨 收到预览试卷请求")
        
        # 获取请求参数
        data = request.json if request.json else {}
        user_id = data.get('user_id')
        max_questions = data.get('max_questions', 10)
        
        # 验证参数
        if not isinstance(max_questions, int) or max_questions < 1 or max_questions > 50:
            return jsonify({
                'success': False,
                'error': '题目数量必须在1-50之间'
            }), 400
            
        logger.info(f"📋 预览参数: user_id={user_id}, max_questions={max_questions}")
        
        # 1. 获取历史记录
        try:
            records = get_records(user_id=user_id)
            logger.info(f"📚 获取到 {len(records)} 条历史记录")
        except Exception as e:
            logger.error(f"❌ 获取历史记录失败: {e}")
            return jsonify({
                'success': False,
                'error': f'获取历史记录失败: {str(e)}'
            }), 500
            
        if not records:
            return jsonify({
                'success': False,
                'error': '没有找到历史记录'
            }), 404
            
        # 2. 提取相似题目
        try:
            generator = get_paper_generator()
            questions = generator.extract_similar_questions_from_history(
                records, 
                max_questions=max_questions
            )
            
            total_found = len(questions)
            will_use = min(total_found, max_questions)
            
            logger.info(f"📊 找到 {total_found} 道题目，将使用 {will_use} 道")
            
            # 3. 返回预览信息
            return jsonify({
                'success': True,
                'questions': questions[:max_questions],
                'total_found': total_found,
                'will_use': will_use,
                'message': f'找到{total_found}道题目，将使用其中{will_use}道'
            }), 200
            
        except Exception as e:
            logger.error(f"❌ 提取题目失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'提取题目失败: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ 处理预览请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@paper_bp.route('/statistics', methods=['GET'])
def get_paper_statistics():
    """
    获取可用题目统计信息
    
    查询参数：
        user_id: 用户ID（可选）
    
    返回：
    {
        "success": true,
        "statistics": {
            "total_records": 10,
            "total_similar_questions": 25,
            "can_generate": true,
            "recommended_count": 10
        }
    }
    """
    try:
        logger.info("📨 收到统计信息请求")
        
        user_id = request.args.get('user_id')
        
        # 获取历史记录
        try:
            records = get_records(user_id=user_id)
        except Exception as e:
            logger.error(f"❌ 获取历史记录失败: {e}")
            return jsonify({
                'success': False,
                'error': f'获取历史记录失败: {str(e)}'
            }), 500
            
        # 提取相似题目
        generator = get_paper_generator()
        questions = generator.extract_similar_questions_from_history(records, max_questions=100)
        
        total_questions = len(questions)
        can_generate = total_questions > 0
        recommended_count = min(total_questions, 10)
        
        logger.info(f"📊 统计: 历史记录={len(records)}, 可用题目={total_questions}")
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_records': len(records),
                'total_similar_questions': total_questions,
                'can_generate': can_generate,
                'recommended_count': recommended_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 处理统计请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@paper_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    
    返回：
    {
        "status": "healthy",
        "service": "paper_generator",
        "font_support": "ok"
    }
    """
    try:
        # 检查字体支持
        from reportlab.pdfbase import pdfmetrics
        
        font_support = "ok"
        try:
            pdfmetrics.getFont('SimSun')
        except:
            font_support = "warning - using default font"
            
        return jsonify({
            'status': 'healthy',
            'service': 'paper_generator',
            'font_support': font_support
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# 错误处理器
@paper_bp.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        'success': False,
        'error': '请求的资源不存在'
    }), 404


@paper_bp.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"❌ 服务器内部错误: {str(error)}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

