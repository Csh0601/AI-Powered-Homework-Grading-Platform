# -*- coding: utf-8 -*-
"""
增强的HuggingFace服务 - 集成新的HuggingFace客户端到现有系统（已弃用）
注意：此服务已被qwen_vl_direct_service替代，推荐使用直接调用LoRA服务
"""
import sys
import os

# 修复Windows编码问题
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import logging
from typing import Dict, Any, List
from ..config import Config

# 导入新的HuggingFace客户端
try:
    from ...huggingface_client import HuggingFaceClient
    HF_CLIENT_AVAILABLE = True
except ImportError:
    try:
        # 尝试从项目根目录导入
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sys.path.insert(0, project_root)
        from huggingface_client import HuggingFaceClient
        HF_CLIENT_AVAILABLE = True
    except ImportError:
        HF_CLIENT_AVAILABLE = False
        print("[WARNING] HuggingFace客户端不可用")

logger = logging.getLogger(__name__)

class EnhancedHuggingFaceService:
    """增强的HuggingFace服务，集成新的客户端"""
    
    def __init__(self):
        self.client = None
        self.service_available = False
        
        if HF_CLIENT_AVAILABLE:
            try:
                self.client = HuggingFaceClient()
                self.service_available = True
                print("[OK] HuggingFace增强服务初始化成功")
            except Exception as e:
                print(f"[ERROR] HuggingFace增强服务初始化失败: {e}")
                self.service_available = False
        else:
            print("[WARNING] HuggingFace客户端不可用，服务将降级")
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.service_available and self.client is not None
    
    def grade_homework(self, question: str, student_answer: str, **kwargs) -> Dict[str, Any]:
        """智能批改作业"""
        if not self.is_available():
            return self._fallback_grading(question, student_answer)
        
        try:
            prompt = f"""
作为专业教师，请批改以下作业：

题目：{question}
学生答案：{student_answer}

请按照以下JSON格式返回结果：
{{
    "correct": true/false,
    "score": 分数(0-100),
    "explanation": "详细批改说明",
    "suggestions": ["改进建议1", "改进建议2"],
    "knowledge_points": ["相关知识点1", "相关知识点2"]
}}

只返回JSON，不要其他内容。
"""
            
            result = self.client.chat_completion(prompt, max_tokens=2000)
            
            if result.get("success"):
                response_text = result.get("response", "")
                try:
                    import json
                    # 尝试提取JSON部分
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        parsed_result = json.loads(json_str)
                        
                        # 标准化结果格式
                        return {
                            "correct": parsed_result.get("correct", False),
                            "score": parsed_result.get("score", 0),
                            "explanation": parsed_result.get("explanation", ""),
                            "suggestions": parsed_result.get("suggestions", []),
                            "knowledge_points": parsed_result.get("knowledge_points", []),
                            "model_used": result.get("model_used", "Unknown"),
                            "service": "Enhanced-HuggingFace"
                        }
                except:
                    # JSON解析失败，使用文本解析
                    return self._parse_text_response(response_text, result.get("model_used"))
            
            return self._fallback_grading(question, student_answer)
            
        except Exception as e:
            logger.error(f"HuggingFace批改失败: {e}")
            return self._fallback_grading(question, student_answer)
    
    def analyze_knowledge_points(self, questions: List[str]) -> List[str]:
        """分析知识点"""
        if not self.is_available():
            return ["基础知识点"]
        
        try:
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            prompt = f"""
分析以下题目涉及的主要知识点：

{questions_text}

请列出3-5个核心知识点，每行一个，格式如下：
- 知识点1
- 知识点2
- 知识点3

只返回知识点列表，不要其他内容。
"""
            
            result = self.client.chat_completion(prompt, max_tokens=500)
            
            if result.get("success"):
                response = result.get("response", "")
                knowledge_points = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        point = line[1:].strip()
                        if point:
                            knowledge_points.append(point)
                
                return knowledge_points[:5] if knowledge_points else ["基础知识点"]
            
        except Exception as e:
            logger.error(f"知识点分析失败: {e}")
        
        return ["基础知识点"]
    
    def generate_practice_questions(self, knowledge_points: List[str], count: int = 3) -> List[Dict[str, Any]]:
        """生成练习题"""
        if not self.is_available():
            return []
        
        try:
            kp_text = "、".join(knowledge_points)
            prompt = f"""
基于知识点"{kp_text}"，生成{count}道适合的练习题。

请按照以下JSON格式返回：
[
    {{
        "question": "题目内容",
        "type": "选择题/填空题/计算题",
        "options": ["A选项", "B选项", "C选项", "D选项"],
        "answer": "正确答案",
        "explanation": "解题思路"
    }}
]

只返回JSON数组，不要其他内容。
"""
            
            result = self.client.chat_completion(prompt, max_tokens=3000)
            
            if result.get("success"):
                response_text = result.get("response", "")
                try:
                    import json
                    # 尝试提取JSON部分
                    start_idx = response_text.find('[')
                    end_idx = response_text.rfind(']') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        questions = json.loads(json_str)
                        return questions
                except:
                    pass
            
        except Exception as e:
            logger.error(f"练习题生成失败: {e}")
        
        return []
    
    def _parse_text_response(self, response_text: str, model_used: str = "Unknown") -> Dict[str, Any]:
        """解析文本响应"""
        import re
        
        # 尝试提取关键信息
        correct = "正确" in response_text or "对" in response_text
        
        # 提取分数
        score_match = re.search(r'(\d+)分', response_text)
        score = int(score_match.group(1)) if score_match else (100 if correct else 0)
        
        return {
            "correct": correct,
            "score": score,
            "explanation": response_text,
            "suggestions": [],
            "knowledge_points": [],
            "model_used": model_used,
            "service": "Enhanced-HuggingFace-TextParsed"
        }
    
    def _fallback_grading(self, question: str, student_answer: str) -> Dict[str, Any]:
        """降级批改方法"""
        return {
            "correct": False,
            "score": 0,
            "explanation": "AI服务暂时不可用，请稍后重试",
            "suggestions": ["请检查网络连接", "稍后重新提交"],
            "knowledge_points": ["基础知识"],
            "model_used": "Fallback",
            "service": "Fallback-Mode"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "Enhanced HuggingFace Service",
            "available": self.is_available(),
            "client_available": HF_CLIENT_AVAILABLE,
            "description": "集成新HuggingFace客户端的增强服务"
        }

# 全局服务实例
enhanced_hf_service = EnhancedHuggingFaceService()

def get_enhanced_hf_service() -> EnhancedHuggingFaceService:
    """获取增强的HuggingFace服务实例"""
    return enhanced_hf_service
