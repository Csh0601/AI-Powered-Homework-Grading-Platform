#!/usr/bin/env python3
"""
Llama服务模块
用于处理与Llama模型的交互
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from app.config import Config

logger = logging.getLogger(__name__)

class LlamaService:
    def __init__(self, model_name: str = "llama2:13b"):
        """
        初始化Llama服务
        
        Args:
            model_name: 使用的模型名称
        """
        self.model_name = model_name
        self.base_url = Config.LLAMA_BASE_URL
        self.timeout = Config.LLAMA_TIMEOUT
        
        # 测试连接
        if not self._test_connection():
            raise Exception("无法连接到Llama服务")
    
    def _test_connection(self) -> bool:
        """测试与Llama服务的连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"连接Llama服务失败: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """
        生成响应
        
        Args:
            prompt: 输入提示
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            生成的响应文本
        """
        try:
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Llama API错误: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            return ""
    
    def analyze_question_type(self, question: str) -> str:
        """
        分析题目类型
        
        Args:
            question: 题目内容
            
        Returns:
            题目类型
        """
        prompt = f"""请分析以下题目的类型，只返回题目类型名称：
        
题目：{question}

请从以下类型中选择一个：
- 选择题
- 判断题  
- 填空题
- 计算题
- 应用题
- 证明题
- 分析题

题目类型："""

        response = self.generate_response(prompt, max_tokens=50, temperature=0.1)
        
        # 提取题目类型
        response = response.strip()
        if any(t in response for t in ['选择题', '单选', '多选']):
            return '选择题'
        elif any(t in response for t in ['判断题', '对错', '是非']):
            return '判断题'
        elif any(t in response for t in ['填空题', '空题']):
            return '填空题'
        elif any(t in response for t in ['计算题', '运算', '计算']):
            return '计算题'
        elif any(t in response for t in ['应用题', '实际应用']):
            return '应用题'
        elif any(t in response for t in ['证明题', '证明']):
            return '证明题'
        elif any(t in response for t in ['分析题', '分析']):
            return '分析题'
        
        return '未知题型'
    
    def grade_question(self, question: str, student_answer: str, question_type: str) -> Dict[str, Any]:
        """
        批改单道题目
        
        Args:
            question: 题目内容
            student_answer: 学生答案
            question_type: 题目类型
            
        Returns:
            批改结果字典
        """
        if question_type == '计算题':
            return self._grade_calculation(question, student_answer)
        elif question_type == '选择题':
            return self._grade_multiple_choice(question, student_answer)
        elif question_type == '判断题':
            return self._grade_true_false(question, student_answer)
        elif question_type == '填空题':
            return self._grade_fill_blank(question, student_answer)
        else:
            return self._grade_general(question, student_answer, question_type)
    
    def _grade_calculation(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改计算题"""
        prompt = f"""作为一名专业的数学老师，请批改以下计算题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-5分
解释：详细的批改说明，包括正确答案和解题过程

如果学生答案错误，请提供正确答案和详细的解题步骤。"""

        response = self.generate_response(prompt, max_tokens=500)
        return self._parse_grading_response(response)
    
    def _grade_multiple_choice(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改选择题"""
        prompt = f"""请批改以下选择题：

题目：{question}
学生选择：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-3分
解释：说明正确答案及选择理由"""

        response = self.generate_response(prompt, max_tokens=300)
        return self._parse_grading_response(response)
    
    def _grade_true_false(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改判断题"""
        prompt = f"""请批改以下判断题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误
分数：0-2分
解释：说明判断理由"""

        response = self.generate_response(prompt, max_tokens=200)
        return self._parse_grading_response(response)
    
    def _grade_fill_blank(self, question: str, student_answer: str) -> Dict[str, Any]:
        """批改填空题"""
        prompt = f"""请批改以下填空题：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误/部分正确
分数：0-3分
解释：说明标准答案及评分理由"""

        response = self.generate_response(prompt, max_tokens=300)
        return self._parse_grading_response(response)
    
    def _grade_general(self, question: str, student_answer: str, question_type: str) -> Dict[str, Any]:
        """通用批改方法"""
        prompt = f"""请批改以下{question_type}：

题目：{question}
学生答案：{student_answer}

请按照以下格式回答：
正确性：正确/错误/部分正确
分数：0-5分
解释：详细的批改说明"""

        response = self.generate_response(prompt, max_tokens=400)
        return self._parse_grading_response(response)
    
    def _parse_grading_response(self, response: str) -> Dict[str, Any]:
        """解析批改响应"""
        result = {
            'correct': False,
            'score': 0,
            'explanation': response
        }
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if '正确性' in line or '结果' in line:
                    if '正确' in line and '错误' not in line:
                        result['correct'] = True
                    elif '部分正确' in line:
                        result['correct'] = True
                elif '分数' in line or '得分' in line:
                    # 提取数字
                    import re
                    scores = re.findall(r'\d+', line)
                    if scores:
                        result['score'] = int(scores[0])
                        
        except Exception as e:
            logger.error(f"解析批改响应失败: {e}")
        
        return result
    
    def analyze_knowledge_points(self, questions: List[Dict]) -> List[str]:
        """
        分析知识点
        
        Args:
            questions: 题目列表
            
        Returns:
            知识点列表
        """
        question_texts = [q.get('question', '') for q in questions]
        all_questions = '\n'.join(question_texts[:5])  # 限制长度
        
        prompt = f"""请分析以下题目涉及的主要知识点：

题目：
{all_questions}

请列出3-5个主要知识点，每行一个："""

        response = self.generate_response(prompt, max_tokens=200)
        
        # 解析知识点
        knowledge_points = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('知识点') and len(line) > 2:
                # 清理格式
                line = line.replace('- ', '').replace('• ', '').replace('1.', '').replace('2.', '').replace('3.', '')
                if line:
                    knowledge_points.append(line)
        
        return knowledge_points[:5]  # 最多返回5个
    
    def generate_practice_questions(self, knowledge_point: str, count: int = 3) -> List[Dict]:
        """
        生成练习题
        
        Args:
            knowledge_point: 知识点
            count: 题目数量
            
        Returns:
            练习题列表
        """
        prompt = f"""基于知识点"{knowledge_point}"，生成{count}道练习题。

请按照以下格式输出：
题目1：[题目内容]
答案1：[标准答案]

题目2：[题目内容]  
答案2：[标准答案]

题目3：[题目内容]
答案3：[标准答案]"""

        response = self.generate_response(prompt, max_tokens=600)
        
        # 解析生成的题目
        questions = []
        lines = response.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('题目'):
                if current_question and 'question' in current_question:
                    questions.append(current_question)
                current_question = {'question': line.split('：', 1)[-1], 'knowledge_point': knowledge_point}
            elif line.startswith('答案'):
                if current_question:
                    current_question['answer'] = line.split('：', 1)[-1]
        
        if current_question and 'question' in current_question:
            questions.append(current_question)
        
        return questions[:count]
