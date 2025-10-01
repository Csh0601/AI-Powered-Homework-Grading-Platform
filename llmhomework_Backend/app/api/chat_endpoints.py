"""
对话API端点
提供前端对话功能的REST API接口
"""

from flask import Blueprint, request, jsonify
import logging
from app.services.chat_service import get_chat_service

logger = logging.getLogger(__name__)

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# 获取对话服务实例
chat_service = get_chat_service()


@chat_bp.route('/start', methods=['POST'])
def start_conversation():
    """
    开始新对话
    
    请求体：
    {
        "task_id": "xxx",
        "grading_result": {...}  # 完整的批改结果
    }
    
    返回：
    {
        "success": true,
        "conversation_id": "conv_xxx_123456",
        "welcome_message": "欢迎消息...",
        "message": "对话已创建"
    }
    """
    try:
        logger.info("📨 收到开始对话请求")
        
        # 验证请求数据
        if not request.json:
            logger.warning("⚠️ 请求体为空")
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
            
        data = request.json
        task_id = data.get('task_id')
        grading_result = data.get('grading_result')
        
        # 验证必要参数
        if not task_id:
            logger.warning("⚠️ 缺少task_id参数")
            return jsonify({
                'success': False,
                'error': '缺少task_id参数'
            }), 400
            
        if not grading_result:
            logger.warning("⚠️ 缺少grading_result参数")
            return jsonify({
                'success': False,
                'error': '缺少grading_result参数'
            }), 400
            
        # 调用服务创建对话
        result = chat_service.start_conversation(task_id, grading_result)
        
        if result['success']:
            logger.info(f"✅ 对话创建成功: conversation_id={result['conversation_id']}")
            return jsonify(result), 200
        else:
            logger.error(f"❌ 对话创建失败: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ 处理开始对话请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    发送消息
    
    请求体：
    {
        "conversation_id": "conv_xxx_123456",
        "message": "用户的问题"
    }
    
    返回：
    {
        "success": true,
        "response": "AI的回答",
        "conversation_id": "conv_xxx_123456",
        "message_count": 5
    }
    """
    try:
        logger.info("📨 收到发送消息请求")
        
        # 验证请求数据
        if not request.json:
            logger.warning("⚠️ 请求体为空")
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
            
        data = request.json
        conversation_id = data.get('conversation_id')
        user_message = data.get('message')
        
        # 验证必要参数
        if not conversation_id:
            logger.warning("⚠️ 缺少conversation_id参数")
            return jsonify({
                'success': False,
                'error': '缺少conversation_id参数'
            }), 400
            
        if not user_message:
            logger.warning("⚠️ 缺少message参数")
            return jsonify({
                'success': False,
                'error': '缺少message参数'
            }), 400
            
        if not isinstance(user_message, str) or not user_message.strip():
            logger.warning("⚠️ 消息内容无效")
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
            
        # 调用服务发送消息
        result = chat_service.send_message(conversation_id, user_message.strip())
        
        if result['success']:
            logger.info(f"✅ 消息发送成功: conversation_id={conversation_id}")
            return jsonify(result), 200
        else:
            logger.error(f"❌ 消息发送失败: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ 处理发送消息请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@chat_bp.route('/history/<conversation_id>', methods=['GET'])
def get_history(conversation_id: str):
    """
    获取对话历史
    
    URL参数：
        conversation_id: 对话会话ID
    
    返回：
    {
        "success": true,
        "messages": [
            {
                "role": "user",
                "content": "问题",
                "timestamp": "2024-..."
            },
            {
                "role": "assistant",
                "content": "回答",
                "timestamp": "2024-..."
            }
        ],
        "message_count": 10
    }
    """
    try:
        logger.info(f"📨 收到获取历史请求: conversation_id={conversation_id}")
        
        # 验证参数
        if not conversation_id or not conversation_id.strip():
            logger.warning("⚠️ conversation_id无效")
            return jsonify({
                'success': False,
                'error': 'conversation_id不能为空'
            }), 400
            
        # 调用服务获取历史
        result = chat_service.get_conversation_history(conversation_id.strip())
        
        if result['success']:
            logger.info(f"✅ 获取历史成功: message_count={result['message_count']}")
            return jsonify(result), 200
        else:
            logger.warning(f"⚠️ 获取历史失败: {result.get('error')}")
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"❌ 处理获取历史请求时发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    
    返回：
    {
        "status": "healthy",
        "service": "chat_service",
        "statistics": {
            "total_tasks": 10,
            "total_conversations": 15,
            "active_conversations": 5
        }
    }
    """
    try:
        from app.services.context_manager import get_context_manager
        
        context_manager = get_context_manager()
        stats = context_manager.get_statistics()
        
        return jsonify({
            'status': 'healthy',
            'service': 'chat_service',
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# 错误处理器
@chat_bp.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        'success': False,
        'error': '请求的资源不存在'
    }), 404


@chat_bp.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"❌ 服务器内部错误: {str(error)}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500
