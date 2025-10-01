"""
对话服务
处理与服务器端的对话交互
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from app.config import Config
from app.services.context_manager import get_context_manager

logger = logging.getLogger(__name__)


class ChatService:
    """处理与Qwen2.5-VL服务器的对话交互"""
    
    def __init__(self):
        """初始化对话服务"""
        self.api_url = getattr(Config, 'QWEN_VL_API_URL', 'http://172.31.179.77:8007')
        self.context_manager = get_context_manager()
        self.timeout = getattr(Config, 'TIMEOUT_SECONDS', 60)
        logger.info(f"✅ 对话服务已初始化，API地址: {self.api_url}")
        
    def start_conversation(self, task_id: str, grading_result: Dict) -> Dict[str, Any]:
        """
        开始新对话
        
        Args:
            task_id: 批改任务ID
            grading_result: 完整的批改结果
            
        Returns:
            包含conversation_id的结果字典
        """
        try:
            # 1. 保存批改上下文
            logger.info(f"📝 开始创建对话: task_id={task_id}")
            self.context_manager.save_grading_context(task_id, grading_result)
            
            # 2. 创建对话会话
            conversation_id = self.context_manager.create_conversation(task_id)
            
            # 3. 生成欢迎消息
            welcome_message = self._generate_welcome_message(grading_result)
            self.context_manager.add_message(conversation_id, 'assistant', welcome_message)
            
            logger.info(f"✅ 对话创建成功: conversation_id={conversation_id}")
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'welcome_message': welcome_message,
                'message': '对话已创建'
            }
            
        except Exception as e:
            logger.error(f"❌ 创建对话失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': '创建对话失败'
            }
            
    def send_message(self, conversation_id: str, user_message: str) -> Dict[str, Any]:
        """
        发送用户消息并获取AI回复
        
        Args:
            conversation_id: 对话会话ID
            user_message: 用户消息内容
            
        Returns:
            包含AI回复的结果字典
        """
        try:
            logger.info(f"💬 发送消息: conversation_id={conversation_id}")
            
            # 1. 验证对话是否存在
            if not self.context_manager.conversation_exists(conversation_id):
                raise ValueError(f"对话不存在: {conversation_id}")
            
            # 2. 添加用户消息到历史
            self.context_manager.add_message(conversation_id, 'user', user_message)
            
            # 3. 获取完整上下文
            full_context = self.context_manager.get_full_context(conversation_id)
            
            # 4. 调用服务器API（暂时使用模拟响应，等服务器端点准备好后替换）
            ai_response = self._call_server_api(full_context, user_message)
            
            # 5. 保存AI回复到历史
            self.context_manager.add_message(conversation_id, 'assistant', ai_response)
            
            logger.info(f"✅ 消息发送成功，已收到AI回复")
            
            return {
                'success': True,
                'response': ai_response,
                'conversation_id': conversation_id,
                'message_count': len(full_context['messages']) + 1
            }
            
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'conversation_id': conversation_id
            }
            
    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """
        获取对话历史
        
        Args:
            conversation_id: 对话会话ID
            
        Returns:
            包含对话历史的结果字典
        """
        try:
            if not self.context_manager.conversation_exists(conversation_id):
                raise ValueError(f"对话不存在: {conversation_id}")
                
            messages = self.context_manager.get_conversation_history(conversation_id)
            
            return {
                'success': True,
                'messages': messages,
                'message_count': len(messages)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取对话历史失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _generate_welcome_message(self, grading_result: Dict) -> str:
        """
        生成欢迎消息
        
        Args:
            grading_result: 批改结果
            
        Returns:
            欢迎消息文本
        """
        try:
            # 提取关键信息
            summary = grading_result.get('summary', {})
            total_questions = summary.get('total_questions', 0)
            correct_count = summary.get('correct_count', 0)
            accuracy_rate = summary.get('accuracy_rate', 0)
            
            # 构建欢迎消息
            welcome = f"你好！我是你的AI学习伙伴 🤖\n\n"
            welcome += f"我刚刚批改了你的作业：\n"
            welcome += f"📊 总题数：{total_questions}题\n"
            welcome += f"✅ 正确：{correct_count}题\n"
            welcome += f"📈 正确率：{accuracy_rate*100:.1f}%\n\n"
            
            if correct_count < total_questions:
                wrong_count = total_questions - correct_count
                welcome += f"还有{wrong_count}道题需要加油哦！\n\n"
            else:
                welcome += f"太棒了，全部答对！🎉\n\n"
                
            welcome += "有什么问题想问我吗？我可以帮你解答疑惑，分析错题原因，提供学习建议哦！"
            
            return welcome
            
        except Exception as e:
            logger.warning(f"⚠️ 生成欢迎消息失败，使用默认消息: {str(e)}")
            return "你好！我是你的AI学习伙伴。我刚刚批改了你的作业，有什么问题想问我吗？"
            
    def _call_server_api(self, full_context: Dict, user_message: str) -> str:
        """
        调用FastAPI服务器端对话API
        
        Args:
            full_context: 完整上下文
            user_message: 用户消息
            
        Returns:
            AI回复内容
        """
        # 尝试调用FastAPI服务器
        try:
            # 准备请求数据（适配FastAPI格式）
            payload = {
                'task_id': full_context['task_id'],
                'conversation_history': full_context['messages'],
                'grading_context': full_context['grading_context']
            }
            
            logger.info(f"📤 发送请求到FastAPI服务器: {self.api_url}/chat")
            
            # 调用FastAPI服务器
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            # FastAPI通常返回JSON格式
            if response.status_code == 200:
                result = response.json()
                
                # 检查FastAPI返回的success字段
                if result.get('success', False):
                    ai_response = result.get('response', '')
                    if ai_response:
                        logger.info(f"✅ FastAPI服务器返回成功，响应长度: {len(ai_response)}")
                        return ai_response
                    else:
                        logger.warning("⚠️ FastAPI返回成功但响应为空")
                        raise Exception("Empty response from server")
                else:
                    # FastAPI返回了错误
                    error_msg = result.get('error', 'Unknown error')
                    logger.warning(f"⚠️ FastAPI返回错误: {error_msg}")
                    raise Exception(f"Server error: {error_msg}")
            else:
                logger.warning(f"⚠️ FastAPI返回HTTP错误: {response.status_code}")
                raise Exception(f"Server returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ 服务器未响应，使用本地智能回复（降级模式）")
            return self._generate_fallback_response(full_context, user_message)
        except requests.exceptions.Timeout:
            logger.warning("⚠️ 服务器响应超时，使用本地智能回复")
            return self._generate_fallback_response(full_context, user_message)
        except Exception as e:
            logger.warning(f"⚠️ 调用服务器API失败: {str(e)}，使用降级响应")
            return self._generate_fallback_response(full_context, user_message)
            
    def _generate_fallback_response(self, full_context: Dict, user_message: str) -> str:
        """
        生成降级响应（当服务器不可用时）
        
        Args:
            full_context: 完整上下文
            user_message: 用户消息
            
        Returns:
            降级响应文本
        """
        grading_context = full_context.get('grading_context', {})
        grading_results = grading_context.get('grading_result', [])
        
        # 简单的关键词匹配响应
        user_message_lower = user_message.lower()
        
        # 检查是否询问错题
        if '错' in user_message or '为什么' in user_message or '怎么' in user_message:
            wrong_questions = [r for r in grading_results if not r.get('correct', True)]
            if wrong_questions:
                response = "让我帮你分析一下错题：\n\n"
                for i, q in enumerate(wrong_questions[:2], 1):  # 只显示前2道
                    response += f"【题目{i}】\n"
                    response += f"题目：{q.get('question', '未知')}\n"
                    response += f"你的答案：{q.get('answer', '未答')}\n"
                    response += f"正确答案：{q.get('correct_answer', '未提供')}\n"
                    response += f"解析：{q.get('explanation', '暂无解析')}\n\n"
                return response
                
        # 检查是否询问知识点
        elif '知识点' in user_message or '考点' in user_message:
            wrong_knowledges = grading_context.get('wrong_knowledges', [])
            if wrong_knowledges:
                return f"根据批改结果，你需要加强以下知识点：\n\n" + "\n".join([f"• {k}" for k in wrong_knowledges])
                
        # 检查是否要建议
        elif '建议' in user_message or '怎么学' in user_message:
            return "学习建议：\n1. 重点复习错题涉及的知识点\n2. 多做类似题目加强练习\n3. 理解概念而不是死记硬背\n4. 遇到不懂的及时问老师"
            
        # 默认响应
        return f"我理解你的问题了。不过目前AI服务器正在升级中，我只能提供基础的回复。\n\n你可以：\n1. 查看详细的批改结果\n2. 复习错题的知识点\n3. 稍后再来和我聊天\n\n有其他问题吗？"


# 创建全局单例实例
_chat_service_instance: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """
    获取对话服务的单例实例
    
    Returns:
        ChatService实例
    """
    global _chat_service_instance
    
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
        
    return _chat_service_instance
