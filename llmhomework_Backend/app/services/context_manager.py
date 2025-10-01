"""
对话上下文管理器
管理批改结果和对话会话的关联
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConversationContextManager:
    """管理对话上下文和批改结果的关联"""
    
    def __init__(self):
        """初始化上下文管理器"""
        # 使用内存存储（生产环境可改用Redis）
        self.task_contexts: Dict[str, Dict] = {}      # task_id -> grading_result
        self.conversations: Dict[str, Dict] = {}      # conversation_id -> conversation_data
        logger.info("✅ 对话上下文管理器已初始化")
        
    def save_grading_context(self, task_id: str, grading_result: Dict) -> None:
        """
        保存批改结果作为对话上下文
        
        Args:
            task_id: 批改任务ID
            grading_result: 完整的批改结果数据
        """
        try:
            self.task_contexts[task_id] = {
                'grading_result': grading_result,
                'timestamp': datetime.now().isoformat(),
                'conversation_count': 0
            }
            logger.info(f"✅ 已保存批改上下文: task_id={task_id}")
        except Exception as e:
            logger.error(f"❌ 保存批改上下文失败: {str(e)}")
            raise
        
    def create_conversation(self, task_id: str) -> str:
        """
        基于批改任务创建对话会话
        
        Args:
            task_id: 批改任务ID
            
        Returns:
            conversation_id: 新创建的对话会话ID
            
        Raises:
            ValueError: 如果task_id不存在
        """
        if task_id not in self.task_contexts:
            logger.error(f"❌ 任务不存在: task_id={task_id}")
            raise ValueError(f"Task {task_id} not found. Please ensure grading context is saved first.")
            
        # 生成唯一的对话ID
        timestamp = int(datetime.now().timestamp() * 1000)  # 使用毫秒时间戳
        conversation_id = f"conv_{task_id}_{timestamp}"
        
        # 创建对话会话
        self.conversations[conversation_id] = {
            'task_id': task_id,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        # 增加任务的对话计数
        self.task_contexts[task_id]['conversation_count'] += 1
        
        logger.info(f"✅ 已创建对话会话: conversation_id={conversation_id}")
        return conversation_id
        
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        添加消息到对话历史
        
        Args:
            conversation_id: 对话会话ID
            role: 消息角色 ('user', 'assistant', 'system')
            content: 消息内容
            
        Raises:
            ValueError: 如果conversation_id不存在
        """
        if conversation_id not in self.conversations:
            logger.error(f"❌ 对话不存在: conversation_id={conversation_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
            
        # 添加消息
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversations[conversation_id]['messages'].append(message)
        self.conversations[conversation_id]['last_activity'] = datetime.now().isoformat()
        
        logger.debug(f"📝 已添加消息: conversation_id={conversation_id}, role={role}, content_length={len(content)}")
        
    def get_full_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        获取完整对话上下文（包括批改结果）
        
        Args:
            conversation_id: 对话会话ID
            
        Returns:
            包含对话历史和批改上下文的完整数据
            
        Raises:
            ValueError: 如果conversation_id不存在
        """
        if conversation_id not in self.conversations:
            logger.error(f"❌ 对话不存在: conversation_id={conversation_id}")
            raise ValueError(f"Conversation {conversation_id} not found")
            
        conv = self.conversations[conversation_id]
        task_id = conv['task_id']
        
        # 组装完整上下文
        full_context = {
            'conversation_id': conversation_id,
            'task_id': task_id,
            'grading_context': self.task_contexts[task_id]['grading_result'],
            'messages': conv['messages'],
            'metadata': {
                'created_at': conv['created_at'],
                'last_activity': conv['last_activity'],
                'message_count': len(conv['messages'])
            }
        }
        
        logger.debug(f"📦 获取完整上下文: conversation_id={conversation_id}, messages={len(conv['messages'])}")
        return full_context
        
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        获取对话历史消息列表
        
        Args:
            conversation_id: 对话会话ID
            
        Returns:
            消息列表
            
        Raises:
            ValueError: 如果conversation_id不存在
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        return self.conversations[conversation_id]['messages']
        
    def conversation_exists(self, conversation_id: str) -> bool:
        """检查对话是否存在"""
        return conversation_id in self.conversations
        
    def task_context_exists(self, task_id: str) -> bool:
        """检查任务上下文是否存在"""
        return task_id in self.task_contexts
        
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'total_tasks': len(self.task_contexts),
            'total_conversations': len(self.conversations),
            'active_conversations': sum(1 for c in self.conversations.values() if len(c['messages']) > 0)
        }
        
    def cleanup_old_conversations(self, max_age_hours: int = 24) -> int:
        """
        清理过期的对话（可选功能）
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的对话数量
        """
        from datetime import timedelta
        
        cleanup_count = 0
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=max_age_hours)
        
        # 找出过期的对话
        expired_conversations = []
        for conv_id, conv_data in self.conversations.items():
            last_activity = datetime.fromisoformat(conv_data['last_activity'])
            if last_activity < cutoff_time:
                expired_conversations.append(conv_id)
                
        # 删除过期对话
        for conv_id in expired_conversations:
            del self.conversations[conv_id]
            cleanup_count += 1
            
        if cleanup_count > 0:
            logger.info(f"🧹 清理了 {cleanup_count} 个过期对话")
            
        return cleanup_count


# 创建全局单例实例
_context_manager_instance: Optional[ConversationContextManager] = None


def get_context_manager() -> ConversationContextManager:
    """
    获取上下文管理器的单例实例
    
    Returns:
        ConversationContextManager实例
    """
    global _context_manager_instance
    
    if _context_manager_instance is None:
        _context_manager_instance = ConversationContextManager()
        
    return _context_manager_instance
